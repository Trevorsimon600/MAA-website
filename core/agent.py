import re
from typing import Optional, Any, Tuple
from v0_2.core.model_router import ModelRouter
from v0_2.core.config import Settings


class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        instructions: str,
        provider: str = "groq",
        tool_registry: Optional[Any] = None
    ):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.router = ModelRouter(provider=provider)
        self.tool_registry = tool_registry
        self.total_tokens_estimated = 0

    def think(self, prompt: str, max_retries: int = 2) -> str:
        """Core thinking execution with tool handling and token tracking."""
        
        # Build system prompt, optionally including tool instructions
        tool_instructions = ""
        if self.tool_registry:
            tool_info = self.tool_registry.get_tool_info()
            tool_instructions = f"""
You have access to tools if needed:
{tool_info}
CRITICAL FOR TOOL USAGE:
Action: tool_name
Action Input: input for tool

When finished or if no tool is needed, provide your final response directly."""
        
        system_prompt = f"{self.instructions}{tool_instructions}"
        
        # Estimate token usage for the initial request
        self.total_tokens_estimated += (len(system_prompt) + len(prompt)) // 4
        
        for attempt in range(max_retries + 1):
            result = self.router.chat(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=Settings.TEMPERATURE
            )
            if result and not result.startswith("Error from"):
                self.total_tokens_estimated += len(result) // 4
                if self.tool_registry and ("Action:" in result and "Action Input:" in result):
                    return self._execute_tool_loop(system_prompt, prompt, result)
                return result
            if attempt < max_retries:
                print(f"   Retry {attempt + 1} for {self.name}...")
        return result or f"[{self.name}] No response generated."

    def _execute_tool_loop(self, system_prompt: str, initial_prompt: str, first_response: str, max_tool_steps: int = 5) -> str:
        history = first_response
        current_response = first_response

        for _ in range(max_tool_steps):
            action_match = re.search(r"Action:\s*(.+)", current_response, re.IGNORECASE)
            input_match = re.search(r"Action Input:\s*(.+)", current_response, re.IGNORECASE)

            if action_match and input_match:
                tool_name = action_match.group(1).strip().lower()
                tool_input = input_match.group(1).strip()

                print(f"   🛠️ [{self.name}] Executing tool: {tool_name} → {tool_input[:70]}...")
                observation = self.tool_registry.use(tool_name, tool_input)

                history += f"\nObservation: {observation[:800]}\n"

                next_prompt = f"{initial_prompt}\n\nPrevious steps:\n{history}\n\nContinue your task or provide final answer."
                self.total_tokens_estimated += (len(system_prompt) + len(next_prompt)) // 4
                current_response = self.router.chat(
                    system_prompt=system_prompt,
                    user_prompt=next_prompt,
                    temperature=Settings.TEMPERATURE
                )
                self.total_tokens_estimated += len(current_response) // 4
                history += f"\n{current_response}\n"
            else:
                break

        return current_response if current_response else history