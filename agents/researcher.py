from core.agent import Agent
from tools.tool_router import use_tool   # temporary fallback
import re

class Researcher(Agent):
    def __init__(self, tool_registry=None):
        super().__init__(
            name="Researcher",
            role="Research Specialist",
            instructions="""You are the Researcher of MAA.

You can use tools when needed.

Available tools:
- search: Search the web for information
- read_page: Read the content of a specific URL
- calculate: Perform simple calculations

When you need a tool, respond exactly in this format:

Thought: reason about what you need
Action: tool_name
Action Input: the input for the tool

When you have enough information, respond with:

Thought: I now have enough information
Final Answer: your complete research summary
"""
        )
        self.tool_registry = tool_registry

    def research(self, objective: str, plan: str = "") -> str:
        """ReAct-style research loop using the Tool Registry when available."""

        max_steps = 5
        history = ""

        for step in range(max_steps):
            prompt = f"""Objective: {objective}

{("Plan context: " + plan[:600]) if plan else ""}

Previous steps:
{history if history else "None"}

Continue the research. Use a tool if needed, or give the Final Answer.
"""

            response = self.think(prompt)

            # Check if the agent wants to use a tool
            action_match = re.search(r"Action:\s*(.+)", response, re.IGNORECASE)
            input_match = re.search(r"Action Input:\s*(.+)", response, re.IGNORECASE)

            if action_match and input_match:
                tool_name = action_match.group(1).strip().lower()
                tool_input = input_match.group(1).strip()

                print(f"   🛠️  Using tool: {tool_name} → {tool_input[:70]}...")

                # Prefer the Tool Registry if available
                if self.tool_registry:
                    observation = self.tool_registry.use(tool_name, tool_input)
                else:
                    # Fallback to old router
                    observation = use_tool(tool_name, tool_input)

                history += f"\nThought/Action:\n{response}\nObservation: {observation[:1300]}\n"
                continue

            # Check for Final Answer
            if "Final Answer:" in response:
                final = response.split("Final Answer:")[-1].strip()
                return final

            # Fallback: treat the whole response as the answer
            return response

        return history[-2000:] if history else "Research could not be completed."