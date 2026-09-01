from v0_2.core.registry import AgentRegistry
from v0_2.core.tool_registry import ToolRegistry
from tasks.manager import TaskManager
from memory.simple_memory import SimpleMemory
from core.project import ProjectManager
from core.message_bus import MessageBus
from core.evaluator import Evaluator
from v0_2.core.config import Settings
from v0_2.core.logger import MAALogger

class OrchestratorV2:
    """
    Cleaner Orchestrator for MAA v0.2.
    Uses Agent Registry + Tool Registry.
    """

    def __init__(self, agent_registry, tool_registry, file_manager=None):
        self.agents = agent_registry
        self.tools = tool_registry
        self.files = file_manager
        self.task_manager = TaskManager()
        self.memory = SimpleMemory()
        self.project_manager = ProjectManager()
        self.message_bus = MessageBus()
        self.evaluator = Evaluator()
        self.logger = MAALogger()

    def _run_agent(self, agent_name: str, prompt: str, task_title: str, objective: str, use_memory: bool = False) -> str:
        agent = self.agents.get(agent_name)

        task = self.task_manager.create_task(
            title=task_title,
            description=f"Task for {agent_name}",
            objective=objective,
            assigned_to=agent_name
        )
        task.start(agent_name)

        # ========== Build context ==========
        context_parts = []

        # Memory
        if use_memory:
            relevant = self.memory.retrieve_relevant_knowledge(objective, max_results=3)
            recent = self.memory.get_memory_summary(max_runs=3)
            context_parts.append(f"Relevant past knowledge:\n{relevant}\n\nRecent runs:\n{recent}")

        # Messages from other agents
        messages = self.message_bus.get_messages_for(agent_name)
        if messages:
            msg_text = "\n".join([str(m) for m in messages[-4:]])
            context_parts.append(f"Messages from other agents:\n{msg_text}")

        # File awareness (IMPORTANT - must be before creating full_prompt)
        if self.files:
            file_context = self.files.get_file_info()
            context_parts.append(f"Currently available files:\n{file_context}")

        # Combine everything
        full_prompt = prompt
        if context_parts:
            full_prompt = "\n\n".join(context_parts) + "\n\n---\n\nCurrent task:\n" + prompt

        print(f"\n→ {agent_name} is working on: {task_title}")

        # Run the agent
        if agent_name == "Researcher" and hasattr(agent, "research"):
            result = agent.research(objective)
        else:
            result = agent.think(full_prompt)

        task.complete(result)
        self.logger.log(agent_name, f"Finished task: {task_title}")

        # Notify other agents
        self.message_bus.send(
            sender=agent_name,
            receiver="ALL",
            content=f"Completed '{task_title}'. Summary: {result[:100]}...",
            msg_type="result"
        )

        print(f"\n{agent_name} output:")
        print(result[:1500] + ("..." if len(result) > 1500 else ""))
        print("-" * 50)

        return result

    def run(self, objective: str, project_id: str = None):
        print("\n" + "=" * 60)
        print(f"🧠 MAA {Settings.VERSION}")
        print("=" * 60)
        print(f"Objective: {objective}\n")
        
        self.logger.start_run(objective)

        # Project context
        project_context = ""
        if project_id:
            project = self.project_manager.get_project(project_id)
            if project:
                project_context = project.get_context()
                print(f"📁 Continuing Project: {project.name}")
                print(project_context)
                print("-" * 50)

        # 1. Planning
        plan_prompt = f"Create a clear and structured plan for this objective:\n{objective}"
        if project_context:
            plan_prompt = f"You are continuing an existing project.\n\n{project_context}\n\nNew objective:\n{objective}\n\nCreate a plan that builds on previous work."

        plan = self._run_agent(
            agent_name="Coordinator",
            prompt=plan_prompt,
            task_title="Create Plan",
            objective=objective,
            use_memory=True
        )

        # 2. Research
        research = self._run_agent(
            agent_name="Researcher",
            prompt=f"Research this objective thoroughly:\n{objective}",
            task_title="Conduct Research",
            objective=objective,
            use_memory=True
        )

        # 3. Critique
        critique = self._run_agent(
            agent_name="Critic",
            prompt=f"""Review the following plan and research. Point out weaknesses and suggest improvements.

PLAN:
{plan}

RESEARCH:
{research}""",
            task_title="Critical Review",
            objective=objective
        )

        # 4. Final Summary
        final = self._run_agent(
            agent_name="Coordinator",
            prompt=f"""Create a clear final answer for the user.

Objective: {objective}

Research:
{research[:1300]}

Critique:
{critique[:900]}

Provide a clean, useful final answer.""",
            task_title="Final Summary",
            objective=objective,
            use_memory=True
        )

        # 5. Verification
        verification = self._run_agent(
            agent_name="Verifier",
            prompt=f"""Original Objective:
{objective}

Final Answer:
{final}

Verify the quality of this answer. Be strict but fair.""",
            task_title="Verify Final Answer",
            objective=objective
        )

        # 6. Evaluation
        print("\n→ Evaluating the run...")
        evaluation = self.evaluator.evaluate(objective, final, verification)
        print(f"   Quality Score: {evaluation.get('score', 'N/A')}/10")

        # Save results
        results = {
            "plan": plan,
            "research": research,
            "critique": critique,
            "final": final,
            "verification": verification,
            "evaluation": evaluation,
            "tasks": self.task_manager.get_all_tasks()
        }

        self.memory.save_run(objective, results)

        if project_id:
            latest = self.memory.get_latest_run()
            if latest:
                self.project_manager.add_run_to_project(project_id, latest.get("run_id"))

        print("\n" + self.task_manager.summary())
        print("All tasks recorded and saved to memory.\n")
        
        self.logger.end_run(evaluation.get("score"))

        return results