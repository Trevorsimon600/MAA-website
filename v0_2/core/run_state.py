import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class RunState:
    """
    Manages and persists the state of an MAA run.
    Supports step metrics, estimated tokens, pausing, resuming, and inspection.
    """

    def __init__(self, run_id: Optional[str] = None, objective: str = "", project_id: Optional[str] = None):
        self.run_id = run_id or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.objective = objective
        self.project_id = project_id
        self.status = "in_progress"  # in_progress | paused | completed | failed
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        self.steps: List[Dict[str, Any]] = []
        self.agent_outputs: Dict[str, str] = {}
        self.messages: List[Dict[str, Any]] = []
        self.quality_score: Optional[float] = None
        self.final_answer: str = ""
        self.total_tokens_estimated: int = 0

    def add_step(
        self,
        step_number: int,
        agent_name: str,
        task_title: str,
        prompt: str,
        output: str,
        status: str = "completed",
        tokens_est: int = 0
    ):
        step_data = {
            "step_number": step_number,
            "agent_name": agent_name,
            "task_title": task_title,
            "prompt": prompt,
            "output": output,
            "status": status,
            "tokens_est": tokens_est,
            "timestamp": datetime.now().isoformat()
        }
        self.steps.append(step_data)
        self.agent_outputs[agent_name] = output
        self.total_tokens_estimated += tokens_est
        self.updated_at = datetime.now().isoformat()

    def record_message(self, sender: str, receiver: str, content: str, msg_type: str = "info"):
        self.messages.append({
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "type": msg_type,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()

    def mark_completed(self, final_answer: str, quality_score: Optional[float] = None):
        self.status = "completed"
        self.final_answer = final_answer
        self.quality_score = quality_score
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "objective": self.objective,
            "project_id": self.project_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "total_steps": len(self.steps),
            "total_tokens_estimated": self.total_tokens_estimated,
            "steps": self.steps,
            "agent_outputs": self.agent_outputs,
            "messages": self.messages,
            "quality_score": self.quality_score,
            "final_answer": self.final_answer
        }

    def save(self, directory: str = "runs"):
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"state_{self.run_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        return filepath

    @classmethod
    def load(cls, run_id: str, directory: str = "runs") -> Optional["RunState"]:
        filepath = os.path.join(directory, f"state_{run_id}.json")
        if not os.path.exists(filepath):
            filepath = os.path.join(directory, f"{run_id}.json")
            if not os.path.exists(filepath):
                return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            state = cls(
                run_id=data.get("run_id"),
                objective=data.get("objective", ""),
                project_id=data.get("project_id")
            )
            state.status = data.get("status", "completed")
            state.created_at = data.get("created_at", datetime.now().isoformat())
            state.updated_at = data.get("updated_at", datetime.now().isoformat())
            state.total_tokens_estimated = data.get("total_tokens_estimated", 0)
            state.steps = data.get("steps", [])
            state.agent_outputs = data.get("agent_outputs", {})
            state.messages = data.get("messages", [])
            state.quality_score = data.get("quality_score")
            state.final_answer = data.get("final_answer", "")
            return state
        except Exception as e:
            print(f"Error loading run state for {run_id}: {e}")
            return None
