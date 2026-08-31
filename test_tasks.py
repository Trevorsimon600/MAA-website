from tasks.manager import TaskManager
from tasks.task import TaskStatus

tm = TaskManager()

task = tm.create_task(
    title="Test Research",
    description="Research multi-agent systems",
    objective="Understand advantages and risks"
)

print(task)
task.start("Researcher")
print(task)
task.complete("Research finished successfully")
print(task)
print(tm.summary())
print("Task system is working!")