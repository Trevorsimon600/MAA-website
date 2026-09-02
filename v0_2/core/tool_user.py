import re
from typing import Optional

class ToolUser:
    """
    Helper that allows any agent to use tools in a simple ReAct style.
    """

    def __init__(self, tool_registry):
        self.tools = tool_registry

    def try_use_tools(self, agent, prompt: str, max_steps: int = 3) -> str:
        """
        Run a simple tool-use loop if the agent decides to use tools.
        """
        history = ""
        current_prompt = prompt

        for step in range(max_steps):
            full_prompt = f"""{current_prompt}

{history}

You have access to tools.
If you need a tool, reply exactly in this format:

Thought: your reasoning
Action: tool_name
Action Input: input for the tool

Available tools: {', '.join(self.tools.list_tools())}

If you don't need any tool, just give your final answer normally.
"""

            response = agent.think(full_prompt)

            # Check for tool call
            action_match = re.search(r"Action:\s*(.+)", response, re.IGNORECASE)
            input_match = re.search(r"Action Input:\s*(.+)", response, re.IGNORECASE)

            if action_match and input_match:
                tool_name = action_match.group(1).strip().lower()
                tool_input = input_match.group(1).strip()

                print(f"   🛠️  {agent.name} is using tool: {tool_name}")

                observation = self.tools.use(tool_name, tool_input)
                history += f"\nAction: {tool_name}\nAction Input: {tool_input}\nObservation: {observation[:1000]}\n"
                continue

            # No tool used → return the response
            return response

        return history or response