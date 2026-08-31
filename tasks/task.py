from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    def __init__(
        self,
        title: str,
        description: str,
        objective: str,
        assigned_to: Optional[str] = None,
        priority: int = 1,
        parent_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.objective = objective
        self.assigned_to = assigned_to
        self.priority = priority
        self.parent_id = parent_id
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self.history: List[Dict[str, Any]] = []

    def start(self, agent_name: str):
        self.status = TaskStatus.IN_PROGRESS
        self.assigned_to = agent_name
        self.updated_at = datetime.now().isoformat()
        self._log(f"Started by {agent_name}")

    def complete(self, result: str):
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.now().isoformat()
        self._log("Completed successfully")

    def fail(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error
        self.updated_at = datetime.now().isoformat()
        self._log(f"Failed: {error}")

    def _log(self, message: str):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "assigned_to": self.assigned_to,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error,
            "history": self.history
        }

    def __str__(self):
        return f"[{self.id}] {self.title} | Status: {self.status.value} | Assigned: {self.assigned_to or 'None'}"