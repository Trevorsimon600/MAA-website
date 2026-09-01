from v0_2.core.registry import AgentRegistry
from v0_2.core.tool_registry import ToolRegistry
from v0_2.core.run_state import RunState
from tasks.manager import TaskManager
from memory.simple_memory import SimpleMemory
from core.project import ProjectManager
from core.message_bus import MessageBus
from core.evaluator import Evaluator
from v0_2.core.config import Settings
from v0_2.core.logger import MAALogger
from typing import Optional, Dict, Any

class OrchestratorV2:
    """
    Dynamic Orchestrator for MAA v0.2.
    Supports dynamic agent scheduling, inter-agent collaboration messages,
    universal tool execution, and persistent RunState.
    """

    def __init__(self, agent_registry: AgentRegistry, tool_registry: ToolRegistry, file_manager=None):
        self.agents = agent_registry
        self.tools = tool_registry
        self.files = file_manager
        self.task_manager = TaskManager()
        self.memory = SimpleMemory()
        self.project_manager = ProjectManager()
        self.message_bus = MessageBus()
        self.evaluator = Evaluator()
        self.logger = MAALogger()

    def _run_agent(
        self,
        agent_name: str,
        prompt: str,
        task_title: str,
        objective: str,
        run_state: Optional[RunState] = None,
        use_memory: bool = False
    ) -> str:
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
            if relevant or recent:
                context_parts.append(f"Relevant past knowledge:\n{relevant}\n\nRecent runs:\n{recent}")

        # Inter-Agent Messages
        messages = self.message_bus.get_messages_for(agent_name)
        if messages:
            msg_text = "\n".join([str(m) for m in messages[-5:]])
            context_parts.append(f"Messages from team:\n{msg_text}")

        # Available files
        if self.files:
            file_context = self.files.get_file_info()
            if file_context:
                context_parts.append(f"Available workspace files:\n{file_context}")

        full_prompt = prompt
        if context_parts:
            full_prompt = "\n\n".join(context_parts) + "\n\n---\n\nCurrent task:\n" + prompt

        print(f"\n→ {agent_name} is working on: {task_title}")

        # Execute agent
        if agent_name == "Researcher" and hasattr(agent, "research"):
            result = agent.research(objective, plan=prompt)
        else:
            result = agent.think(full_prompt)

        task.complete(result)
        self.logger.log(agent_name, f"Completed: {task_title}")

        # Record step in RunState
        if run_state:
            step_num = len(run_state.steps) + 1
            run_state.add_step(step_num, agent_name, task_title, prompt, result)
            run_state.save()

        # Send result notification across MessageBus
        self.message_bus.send(
            sender=agent_name,
            receiver="ALL",
            content=f"Finished '{task_title}'. Output summary: {result[:120]}...",
            msg_type="result"
        )

        print(f"\n{agent_name} output:")
        print(result[:1200] + ("..." if len(result) > 1200 else ""))
        print("-" * 50)

        return result

    def run(self, objective: str, project_id: str = None, max_steps: int = 6) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print(f"🧠 MAA {Settings.VERSION} (Dynamic Orchestration)")
        print("=" * 60)
        print(f"Objective: {objective}\n")

        self.logger.start_run(objective)
        run_state = RunState(objective=objective, project_id=project_id)

        # Project Context
        project_context = ""
        if project_id:
            project = self.project_manager.get_project(project_id)
            if project:
                project_context = project.get_context()
                print(f"📁 Project Context Loaded: {project.name}")

        coordinator = self.agents.get("Coordinator")

        # Dynamic loop execution
        step_count = 0

        while step_count < max_steps:
            step_count += 1

            # Let Coordinator decide the next action based on current state
            decision = coordinator.decide_next_action(
                objective=objective,
                steps_taken=run_state.steps,
                message_history=self.message_bus.to_list()
            )

            status = decision.get("status", "CONTINUE")
            next_agent = decision.get("next_agent", "Researcher")
            task_title = decision.get("task_title", f"Dynamic Step {step_count}")
            instructions = decision.get("instructions", objective)

            if status == "COMPLETE" or next_agent == "Coordinator" and step_count > 1:
                print("\n🎯 Coordinator concluded the dynamic execution graph.")
                break

            # Execute decided agent step
            self._run_agent(
                agent_name=next_agent,
                prompt=instructions,
                task_title=task_title,
                objective=objective,
                run_state=run_state,
                use_memory=(step_count == 1)
            )

        # Final Verification & Summary Step
        final_summary = self._run_agent(
            agent_name="Coordinator",
            prompt=f"Provide the final comprehensive answer for objective:\n{objective}",
            task_title="Final Summary",
            objective=objective,
            run_state=run_state,
            use_memory=True
        )

        verifier = self.agents.get("Verifier")
        verification = verifier.think(f"Objective: {objective}\nFinal Answer:\n{final_summary}")
        
        # Evaluate run
        print("\n→ Evaluating execution score...")
        evaluation = self.evaluator.evaluate(objective, final_summary, verification)
        score = evaluation.get("score", 8.0)
        print(f"   Quality Score: {score}/10")

        run_state.mark_completed(final_summary, quality_score=score)
        run_state.save()

        # Save to memory and project
        results = {
            "run_id": run_state.run_id,
            "objective": objective,
            "final": final_summary,
            "verification": verification,
            "evaluation": evaluation,
            "steps": run_state.steps,
            "messages": run_state.messages,
            "tasks": self.task_manager.get_all_tasks()
        }

        self.memory.save_run(objective, results)
        if project_id:
            self.project_manager.add_run_to_project(project_id, run_state.run_id)

        self.logger.end_run(score)
        print("\n" + self.task_manager.summary())
        return results

    def resume_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        run_state = RunState.load(run_id)
        if not run_state:
            print(f"Error: Run state '{run_id}' not found.")
            return None

        print(f"\n🔄 Resuming run {run_id} for objective: {run_state.objective}")
        return self.run(run_state.objective, project_id=run_state.project_id)