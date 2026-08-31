import os
from typing import Optional
from groq import Groq
from openai import OpenAI
from v0_2.core.config import Settings

class ModelRouter:
    """
    Simple model router for MAA v0.2.
    Supports Groq and OpenAI.
    """

    def __init__(self, provider: str = "groq", model: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model

        if self.provider == "groq":
            self.client = Groq(api_key=Settings.GROQ_API_KEY)
            self.model = model or Settings.DEFAULT_MODEL
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is missing in your .env file")
            self.client = OpenAI(api_key=api_key)
            self.model = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'groq' or 'openai'.")

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Send a chat request to the selected provider."""

        try:
            if self.provider == "groq":
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