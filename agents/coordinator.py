from core.agent import Agent
import json
import re

class Coordinator(Agent):
    def __init__(self):
        super().__init__(
            name="Coordinator",
            role="Chief Coordinator of MAA",
            instructions="""You are the Coordinator of the Mega Agent Association (MAA).

Your responsibilities:
1. Understand the overall objective clearly
2. Break it into logical steps
3. Decide which specialist should handle each step
4. Keep the team focused
5. Produce clean final summaries

Be decisive, structured, and concise."""
        )

    def create_task_plan(self, objective: str) -> list:
        """Ask the Coordinator to generate a dynamic list of tasks."""
        
        prompt = f"""Create a short task plan for this objective:

Objective: {objective}

Available agents:
- Planner (good at creating structured plans and strategies)
- Researcher (good at gathering information and analysis)
- Critic (good at finding weaknesses)
- Verifier (good at checking quality)
- Archivist (good at summarizing and preserving knowledge)
- Analyst (good at deep analysis and comparison)
- Writer (good at clear, structured writing)

Return ONLY a valid JSON list like this example:

[
  {{"title": "Research the topic", "agent": "Researcher", "description": "Gather key information"}},
  {{"title": "Critical review", "agent": "Critic", "description": "Find weaknesses"}},
  {{"title": "Final verification", "agent": "Verifier", "description": "Check the quality"}}
]

Rules:
- Maximum 4 tasks
- Only use the agents listed above
- Keep titles short
- Return pure JSON only (no extra text)
"""

        response = self.think(prompt)
        
        # Try to extract JSON from the response
        try:
            # Find JSON array in the response
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                tasks = json.loads(match.group())
                return tasks
            else:
                # Fallback plan
                return self._fallback_plan()
        except Exception:
            return self._fallback_plan()

    def _fallback_plan(self):
        """Safe default plan if JSON parsing fails."""
        return [
            {"title": "Conduct Research", "agent": "Researcher", "description": "Gather information"},
            {"title": "Critical Review", "agent": "Critic", "description": "Find weaknesses"},
            {"title": "Verify Quality", "agent": "Verifier", "description": "Check final quality"}
        ]