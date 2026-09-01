import os
import json
import re
from typing import Optional, List
from groq import Groq
from openai import OpenAI
from v0_2.core.config import Settings

class ModelRouter:
    """
    Robust model router for MAA v0.2.
    Supports Groq and OpenAI with automatic recovery for Groq tool calling exceptions
    and automatic fallback across available models.
    """

    def __init__(self, provider: str = "groq", model: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model or Settings.DEFAULT_MODEL
        self.fallback_models: List[str] = getattr(Settings, "FALLBACK_MODELS", [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "qwen/qwen3.6-27b"
        ])

        if self.provider == "groq":
            self.client = Groq(api_key=Settings.GROQ_API_KEY)
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is missing in your .env file")
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'groq' or 'openai'.")

    def _call_groq_with_fallback(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Attempt API call with active model and rotate fallback models on rate limits or 404 errors."""
        
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]

        for target_model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=2048
                )
                if target_model != self.model:
                    print(f"   🔄 [ModelRouter] Switched to available model: {target_model}")
                    self.model = target_model
                return response.choices[0].message.content.strip()

            except Exception as e:
                err_msg = str(e)

                # Direct inspection of Groq BadRequestError body for failed tool call
                body = getattr(e, "body", None)
                if isinstance(body, dict) and "error" in body and isinstance(body["error"], dict):
                    fg = body["error"].get("failed_generation")
                    if fg:
                        try:
                            tool_data = json.loads(fg) if isinstance(fg, str) else fg
                            name = tool_data.get("name", "search")
                            args = tool_data.get("arguments", {})
                            query = ""
                            if isinstance(args, dict):
                                query = args.get("query") or args.get("input") or args.get("prompt") or (list(args.values())[0] if args else "")
                            elif isinstance(args, str):
                                query = args

                            if name and query:
                                print(f"   ℹ️ [ModelRouter] Recovered Groq tool call: {name} → {str(query)[:60]}")
                                return f"Thought: I need to use the {name} tool.\nAction: {name}\nAction Input: {query}"
                        except Exception as pe:
                            print(f"   ⚠️ Could not parse failed_generation body: {pe}")

                # If rate limit (429) or model not found (404) hit, try next fallback model
                if any(k in err_msg.lower() for k in ["rate_limit_exceeded", "429", "tokens per day", "model_not_found", "does not exist", "404"]):
                    print(f"   ⚠️ Model '{target_model}' unavailable or rate-limited. Trying next model...")
                    continue
                else:
                    return f"Error from {self.provider}: {str(e)}"

        return f"Error from {self.provider}: All Groq fallback models failed."

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Send a chat request to the selected provider."""

        try:
            if self.provider == "groq":
                return self._call_groq_with_fallback(system_prompt, user_prompt, temperature)

            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=2048
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error from {self.provider}: {str(e)}"