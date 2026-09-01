from core.agent import Agent
import json
import re
from typing import Dict, List, Any

class Coordinator(Agent):
    def __init__(self, tool_registry=None):
        super().__init__(
            name="Coordinator",
            role="Chief Coordinator of MAA",
            instructions="""You are the Coordinator of the Mega Agent Association (MAA).

Your responsibilities:
1. Understand the overall objective clearly
2. Dynamically orchestrate specialists based on context and current progress
3. Evaluate previous outputs, critique feedback, and help requests
4. Decide the single next best step and agent, or complete the run
5. Produce clean, comprehensive final summaries

Be decisive, strategic, structured, and concise.""",
            tool_registry=tool_registry
        )

    def decide_next_action(
        self,
        objective: str,
        steps_taken: List[Dict[str, Any]],
        message_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically decide the next step in an active run loop.
        Returns a dictionary:
        {"status": "CONTINUE", "next_agent": "Researcher", "task_title": "...", "instructions": "..."}
        OR
        {"status": "COMPLETE", "final_summary_prompt": "..."}
        """

        summary_steps = ""
        for s in steps_taken:
            summary_steps += f"- Step {s.get('step_number')}: [{s.get('agent_name')}] Task: {s.get('task_title')}\n  Output Summary: {str(s.get('output', ''))[:300]}...\n"

        msgs = ""
        if message_history:
            msgs = "Recent Inter-Agent Messages:\n" + "\n".join([f"[{m.get('type', 'info')}] {m.get('sender')} -> {m.get('receiver')}: {m.get('content')}" for m in message_history[-4:]])

        prompt = f"""You are coordinating an objective in real time.

Objective: {objective}

Steps completed so far:
{summary_steps if summary_steps else "None yet."}

{msgs}

Available agents to assign next:
- Planner: Create or adjust execution strategy
- Researcher: Gather facts, web research, read files
- Analyst: Synthesize data, compare options, evaluate tradeoffs
- Critic: Point out flaws, missing facts, weak assumptions
- Verifier: Verify accuracy, logical consistency, score response
- Writer: Produce polished documentation, summaries, reports
- Archivist: Summarize knowledge for long-term storage

Evaluate the current state. Should we call another agent or produce the final summary?

Respond EXACTLY in one of these two JSON formats:

If more work is needed:
{{
  "status": "CONTINUE",
  "next_agent": "AgentName",
  "task_title": "Short Task Title",
  "instructions": "Specific instructions for what this agent should do next"
}}

If objective is sufficiently answered:
{{
  "status": "COMPLETE",
  "next_agent": "Coordinator",
  "task_title": "Final Summary",
  "instructions": "Create the final comprehensive response"
}}

Return ONLY valid JSON.
"""

        response = self.think(prompt)

        try:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                decision = json.loads(match.group())
                if "status" in decision and "next_agent" in decision:
                    return decision
        except Exception as e:
            print(f"   ⚠️ Coordinator decision parse error: {e}")

        # Fallback heuristic logic based on steps taken
        step_count = len(steps_taken)
        if step_count == 0:
            return {"status": "CONTINUE", "next_agent": "Researcher", "task_title": "Conduct Research", "instructions": f"Research key information for: {objective}"}
        elif step_count == 1:
            return {"status": "CONTINUE", "next_agent": "Analyst", "task_title": "Analyze Information", "instructions": f"Analyze findings and identify key options/tradeoffs for: {objective}"}
        elif step_count == 2:
            return {"status": "CONTINUE", "next_agent": "Critic", "task_title": "Critical Review", "instructions": "Identify flaws, gaps, or weak points."}
        elif step_count == 3:
            return {"status": "CONTINUE", "next_agent": "Verifier", "task_title": "Verify Results", "instructions": "Verify accuracy and assess answer quality."}
        else:
            return {"status": "COMPLETE", "next_agent": "Coordinator", "task_title": "Final Summary", "instructions": "Synthesize all agent outputs into a final clean answer."}

    def create_task_plan(self, objective: str) -> list:
        prompt = f"""Create a short task plan for this objective:

Objective: {objective}

Available agents: Planner, Researcher, Analyst, Writer, Critic, Verifier, Archivist.

Return ONLY a valid JSON list:
[
  {{"title": "Research", "agent": "Researcher", "description": "Gather info"}},
  {{"title": "Analyze", "agent": "Analyst", "description": "Deep analysis"}},
  {{"title": "Verify", "agent": "Verifier", "description": "Check quality"}}
]
"""
        response = self.think(prompt)
        try:
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

        return [
            {"title": "Conduct Research", "agent": "Researcher", "description": "Gather information"},
            {"title": "Analyze Findings", "agent": "Analyst", "description": "Synthesize data"},
            {"title": "Verify Quality", "agent": "Verifier", "description": "Check final quality"}
        ]