import re
from typing import Optional, Any
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

    def think(self, prompt: str, max_retries: int = 2) -> str:
        # If agent has tools and prompt suggests using tools or universal tool usage, route to think_with_tools
        if self.tool_registry and ("Action:" in prompt or "tool" in prompt.lower()):
            return self.think_with_tools(prompt)

        tool_instructions = ""
        if self.tool_registry:
            tool_info = self.tool_registry.get_tool_info()
            tool_instructions = f"""\n\nYou have access to tools if needed:\n{tool_info}\n
To use a tool, respond with:
Thought: your reasoning
Action: tool_name
Action Input: input for tool

When finished, provide your answer normally."""

        system_prompt = f"""You are {self.name}, the {self.role}.

{self.instructions}{tool_instructions}

Always respond helpfully, accurately, and clearly.
"""

        for attempt in range(max_retries + 1):
            result = self.router.chat(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=Settings.TEMPERATURE
            )

            if result and not result.startswith("Error from"):
                # If the agent decided to use a tool mid-response
                if self.tool_registry and ("Action:" in result and "Action Input:" in result):
                    return self._execute_tool_loop(prompt, result)
                return result

            if attempt < max_retries:
                print(f"   Retry {attempt + 1} for {self.name}...")

        return result or f"[{self.name}] No response generated."

    def _execute_tool_loop(self, initial_prompt: str, first_response: str, max_steps: int = 4) -> str:
        history = first_response
        current_response = first_response

        for _ in range(max_steps):
            action_match = re.search(r"Action:\s*(.+)", current_response, re.IGNORECASE)
            input_match = re.search(r"Action Input:\s*(.+)", current_response, re.IGNORECASE)

            if action_match and input_match:
                tool_name = action_match.group(1).strip().lower()
                tool_input = input_match.group(1).strip()

                print(f"   🛠️ [{self.name}] Using tool: {tool_name} → {tool_input[:70]}...")
                observation = self.tool_registry.use(tool_name, tool_input)

                history += f"\nObservation: {observation[:1200]}\n"

                next_prompt = f"{initial_prompt}\n\nPrevious steps:\n{history}\n\nContinue your task or provide final answer."
                current_response = self.router.chat(
                    system_prompt=f"You are {self.name}, the {self.role}. Continue reasoning.",
                    user_prompt=next_prompt,
                    temperature=Settings.TEMPERATURE
                )
                history += f"\n{current_response}\n"
            else:
                break

        return current_response if current_response else history

    def think_with_tools(self, prompt: str, max_steps: int = 4) -> str:
        if not self.tool_registry:
            return self.think(prompt)

        return self._execute_tool_loop(prompt, self.think(prompt), max_steps=max_steps)