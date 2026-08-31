from tasks.task import Task, TaskStatus
from typing import List, Optional, Dict

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(
        self,
        title: str,
        description: str,
        objective: str,
        assigned_to: Optional[str] = None,
        priority: int = 1
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            objective=objective,
            assigned_to=assigned_to,
            priority=priority
        )
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]

    def get_completed_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]

    def summary(self) -> str:
        total = len(self.tasks)
        pending = len(self.get_pending_tasks())
        completed = len(self.get_completed_tasks())
        failed = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])

        return f"Tasks → Total: {total} | Pending: {pending} | Completed: {completed} | Failed: {failed}"