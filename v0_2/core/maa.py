from v0_2.core.config import Settings
from v0_2.core.registry import AgentRegistry
from v0_2.core.tool_registry import ToolRegistry
from v0_2.core.orchestrator import OrchestratorV2
from v0_2.core.file_manager import FileManager
from v0_2.core.run_state import RunState
from core.project import ProjectManager
from memory.simple_memory import SimpleMemory

from agents.coordinator import Coordinator
from agents.analyst import Analyst
from agents.writer import Writer
from agents.planner import Planner
from agents.researcher import Researcher
from agents.critic import Critic
from agents.verifier import Verifier
from agents.archivist import Archivist


class MAA:
    """
    MAA v0.2 - Mega Agent Association (Phase 1 Upgraded)
    """

    def __init__(self):
        Settings.validate()

        self.version = Settings.VERSION
        self.registry = AgentRegistry()
        self.tools = ToolRegistry()
        self.memory = SimpleMemory()
        self.files = FileManager()
        self.project_manager = ProjectManager()

        # Register ALL agents with universal tool access
        self._register_agents()

        # Create orchestrator after agents are registered
        self.orchestrator = OrchestratorV2(
            agent_registry=self.registry,
            tool_registry=self.tools,
            file_manager=self.files
        )

    def _register_agents(self):
        self.registry.register("Coordinator", Coordinator(tool_registry=self.tools))
        self.registry.register("Planner", Planner(tool_registry=self.tools))
        self.registry.register("Researcher", Researcher(tool_registry=self.tools))
        self.registry.register("Critic", Critic(tool_registry=self.tools))
        self.registry.register("Verifier", Verifier(tool_registry=self.tools))
        self.registry.register("Analyst", Analyst(tool_registry=self.tools))
        self.registry.register("Writer", Writer(tool_registry=self.tools))
        self.registry.register("Archivist", Archivist(tool_registry=self.tools))

    def run(self, objective: str, project_id: str = None, max_steps: int = 6):
        print(f"\n🧠 MAA {self.version}")
        print("=" * 60)
        return self.orchestrator.run(objective, project_id=project_id, max_steps=max_steps)

    def resume_run(self, run_id: str):
        return self.orchestrator.resume_run(run_id)

    def get_run_state(self, run_id: str):
        return RunState.load(run_id)

    def status(self) -> dict:
        return {
            "version": self.version,
            "agents": self.registry.list_agents(),
            "tools": self.tools.list_tools(),
            "projects": len(self.project_manager.list_projects()),
            "runs": len(self.memory.list_runs()),
            "status": "operational"
        }

    def list_agents(self):
        return self.registry.list_agents()

    def create_project(self, name: str, goal: str):
        return self.project_manager.create_project(name, goal)

    def list_projects(self):
        return self.project_manager.list_projects()
    
    def list_files(self):
        return self.files.list_uploaded_files()

    def list_images(self):
        return self.files.list_generated_images()

    def read_file(self, filename: str):
        return self.files.read_text_file(filename)