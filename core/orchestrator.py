from agents.coordinator import Coordinator
from agents.researcher import Researcher
from agents.critic import Critic
from agents.verifier import Verifier
from tasks.manager import TaskManager
from memory.simple_memory import SimpleMemory
from agents.planner import Planner
from agents.archivist import Archivist
from core.evaluator import Evaluator
from core.project import ProjectManager
from core.message_bus import MessageBus
from core.config import Config

class Orchestrator:
    def __init__(self):
        self.task_manager = TaskManager()
        self.memory = SimpleMemory()
        self.evaluator = Evaluator()
        self.project_manager = ProjectManager()
        self.message_bus = MessageBus()

        self.agents = {
            "Coordinator": Coordinator(),
            "Researcher": Researcher(),
            "Critic": Critic(),
            "Verifier": Verifier(),
            "Planner": Planner(),
            "Archivist": Archivist()
        }

    def _run_agent(self, agent_name: str, prompt: str, task_title: str, objective: str, use_memory: bool = False) -> str:
        agent = self.agents.get(agent_name)
        if not agent:
            return f"Error: Agent {agent_name} not found."

        task = self.task_manager.create_task(
            title=task_title,
            description=f"Task for {agent_name}",
            objective=objective,
            assigned_to=agent_name
        )
        task.start(agent_name)

        # Collect messages for this agent
        messages = self.message_bus.get_messages_for(agent_name)
        message_context = ""
        if messages:
            message_context = "Messages from other agents:\n" + "\n".join([str(m) for m in messages[-5:]])

        full_prompt = prompt

        if use_memory or message_context:
            memory_part = ""
            if use_memory:
                recent = self.memory.get_memory_summary(max_runs=3)
                relevant = self.memory.retrieve_relevant_knowledge(objective, max_results=3)
                memory_part = f"{relevant}\n\nRecent runs:\n{recent}"

            full_prompt = f"""{memory_part}

    {message_context}

    ---

    Current task:
    {prompt}"""

        print(f"\n→ {agent_name} is working on: {task_title}")

        if agent_name == "Researcher" and hasattr(agent, "research"):
            result = agent.research(objective)
        else:
            result = agent.think(full_prompt)

        task.complete(result)

        # Let the agent send a short message to the next agents
        self.message_bus.send(
            sender=agent_name,
            receiver="ALL",
            content=f"Completed '{task_title}'. Key point: {result[:120]}...",
            msg_type="result"
        )

        print(f"\n{agent_name} output:")
        print(result)
        print("-" * 50)

        return result


    def run(self, objective: str, project_id: str = None):
        print("\n" + "=" * 60)
        print("🧠 MAA v0.1 – Mega Agent Association")
        print("=" * 60)
        print(f"Objective: {objective}\n")

        project_context = ""
        if project_id:
            project = self.project_manager.get_project(project_id)
            if project:
                project_context = project.get_context()
                print(f"📁 Continuing Project: {project.name}")
                print(project_context)
                print("-" * 50)

        # 1. Coordinator creates a dynamic task plan
        print("→ Coordinator is creating a task plan...")

        plan_prompt = f"Create a clear plan for this objective:\n{objective}"

        if project_context:
            plan_prompt = (
                "You are continuing an existing project.\n\n"
                f"{project_context}\n\n"
                f"New objective:\n{objective}\n\n"
                "Create a clear plan that builds on the previous work."
            )

        task_plan = self._run_agent(
            agent_name="Coordinator",
            prompt=plan_prompt,
            task_title="Create Plan",
            objective=objective,
            use_memory=True
        )

        print("\nCoordinator Plan:")
        print(task_plan)
        print("-" * 50)

        results = {
            "plan": str(task_plan),
            "research": "",
            "critique": "",
            "final": "",
            "verification": ""
        }

        # ========================================================
        # 2. EXECUTE RESEARCH
        # ========================================================

        research = self._run_agent(
            agent_name="Researcher",
            prompt=f"""Research the following objective thoroughly.

Objective:
{objective}

Coordinator plan:
{task_plan}

Provide:
- Key findings
- Advantages
- Risks
- Challenges
- Limitations
- Relevant evidence

Use real web research where available.""",
            task_title="Conduct Research",
            objective=objective,
            use_memory=True
        )

        results["research"] = research

        # ========================================================
        # 3. CRITIC REVIEW
        # ========================================================

        critique = self._run_agent(
            agent_name="Critic",
            prompt=f"""Critically review the research below.

Objective:
{objective}

Research:
{research}

Identify:
- Weak assumptions
- Missing information
- Contradictions
- Unsupported claims
- Important risks
- Areas that need improvement

Give constructive feedback.""",
            task_title="Critically Review Research",
            objective=objective,
            use_memory=True
        )

        results["critique"] = critique

        # ========================================================
        # 4. VERIFICATION
        # ========================================================

        verification = self._run_agent(
            agent_name="Verifier",
            prompt=f"""Verify the research and critique below.

Objective:
{objective}

Research:
{research}

Critique:
{critique}

Check:
- Accuracy
- Completeness
- Logical consistency
- Unsupported claims
- Whether the objective was actually answered

Provide a verification report and confidence assessment.""",
            task_title="Verify Results",
            objective=objective,
            use_memory=True
        )

        results["verification"] = verification

        # 3. Final summary by Coordinator
        final = self._run_agent(
            agent_name="Coordinator",
            prompt=f"""Create a clear final summary for the user based on all the work done.

Objective: {objective}

Research:
{results.get('research', '')[:1200]}

Critique:
{results.get('critique', '')[:1000]}

Verification:
{results.get('verification', '')[:800]}

Provide a clean, useful final answer.""",
            task_title="Final Summary",
            objective=objective,
            use_memory=True
        )
        results["final"] = final
        
        # Evaluation
        print("\n→ Evaluating the run...")
        evaluation = self.evaluator.evaluate(
            objective=objective,
            final_answer=results.get("final", ""),
            verification=results.get("verification", "")
        )
        results["evaluation"] = evaluation
        print(f"   Quality Score: {evaluation['score']}/10")

        # 4. Save to memory
        results["tasks"] = self.task_manager.get_all_tasks()
        self.memory.save_run(objective, results)

        # Link to project if provided
        if project_id:
            run_id = None
            # Try to get the run_id that was just saved
            latest = self.memory.get_latest_run()
            if latest:
                run_id = latest.get("run_id")
                self.project_manager.add_run_to_project(project_id, run_id)
                print(f"📁 Run linked to project: {project_id}")

        print("\n" + self.task_manager.summary())
        print("All tasks recorded and saved to memory.\n")

        return results