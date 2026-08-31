import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class Project:
    def __init__(self, name: str, goal: str, project_id: str = None):
        self.id = project_id or str(uuid.uuid4())[:8]
        self.name = name
        self.goal = goal
        self.status = "active"          # active | completed | paused
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.run_ids: List[str] = []
        self.notes: List[str] = []      # Simple notes / lessons

    def add_run(self, run_id: str):
        if run_id not in self.run_ids:
            self.run_ids.append(run_id)
            self.updated_at = datetime.now().isoformat()

    def add_note(self, note: str):
        self.notes.append(f"{datetime.now().strftime('%Y-%m-%d')}: {note}")
        self.updated_at = datetime.now().isoformat()

    def get_context(self) -> str:
        """Return a short context summary for continuing work on this project."""
        context = f"Project: {self.name}\nGoal: {self.goal}\nStatus: {self.status}\n"
        context += f"Number of previous runs: {len(self.run_ids)}\n"
        if self.notes:
            context += "Recent notes:\n" + "\n".join(self.notes[-3:])
        return context

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "run_ids": self.run_ids,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict):
        project = cls(
            name=data["name"],
            goal=data["goal"],
            project_id=data["id"]
        )
        project.status = data.get("status", "active")
        project.created_at = data.get("created_at", datetime.now().isoformat())
        project.updated_at = data.get("updated_at", project.created_at)
        project.run_ids = data.get("run_ids", [])
        project.notes = data.get("notes", [])
        return project


class ProjectManager:
    def __init__(self, storage_file: str = "projects.json"):
        self.storage_file = storage_file
        self.projects: Dict[str, Project] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for p in data.get("projects", []):
                        project = Project.from_dict(p)
                        self.projects[project.id] = project
            except Exception:
                self.projects = {}

    def _save(self):
        data = {
            "projects": [p.to_dict() for p in self.projects.values()]
        }
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_project(self, name: str, goal: str) -> Project:
        project = Project(name=name, goal=goal)
        self.projects[project.id] = project
        self._save()
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.projects.get(project_id)

    def list_projects(self) -> List[Project]:
        return list(self.projects.values())

    def add_run_to_project(self, project_id: str, run_id: str):
        project = self.get_project(project_id)
        if project:
            project.add_run(run_id)
            self._save()

    def add_note_to_project(self, project_id: str, note: str):
        project = self.get_project(project_id)
        if project:
            project.add_note(note)
            self._save()