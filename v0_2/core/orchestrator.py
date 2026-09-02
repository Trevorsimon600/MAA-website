from v0_2.core.registry import AgentRegistry
from v0_2.core.tool_registry import ToolRegistry
from v0_2.core.run_state import RunState
from v0_2.core.collaboration import detect_help_request
from v0_2.core.tool_user import ToolUser
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
    Supports uninhibited dynamic agent scheduling, inter-agent collaboration messages,
    universal tool execution, step count telemetry, and estimated token tracking.
    """

    def __init__(self, agent_registry: AgentRegistry, tool_registry: ToolRegistry, file_manager=None, knowledge_graph=None):
        self.agents = agent_registry
        self.tools = tool_registry
        self.files = file_manager
        self.knowledge_graph = knowledge_graph
        self.tool_user = ToolUser(tool_registry)
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
        tokens_before = getattr(agent, "total_tokens_estimated", 0)

        task = self.task_manager.create_task(
            title=task_title,
            description=f"Task for {agent_name}",
            objective=objective,
            assigned_to=agent_name
        )
        task.start(agent_name)

        # ========== Build context ==========
        context_parts = []

        if use_memory:
            relevant = self.memory.retrieve_relevant_knowledge(objective, max_results=3)
            recent = self.memory.get_memory_summary(max_runs=3)
            if relevant or recent:
                context_parts.append(f"Relevant past knowledge:\n{relevant}\n\nRecent runs:\n{recent}")

        messages = self.message_bus.get_messages_for(agent_name)
        if messages:
            msg_text = "\n".join([str(m) for m in messages[-5:]])
            context_parts.append(f"Messages from team:\n{msg_text}")

        if self.files:
            file_context = self.files.get_file_info()
            if file_context:
                context_parts.append(f"Available workspace files:\n{file_context}")
                
                

        full_prompt = prompt
        if context_parts:
            full_prompt = "\n\n".join(context_parts) + "\n\n---\n\nCurrent task:\n" + prompt

        print(f"\n→ {agent_name} is working on: {task_title}")
        
        # Knowledge Graph retrieval
        if self.knowledge_graph:
            kg_results = self.knowledge_graph.search(objective, max_results=4)
            if "No relevant knowledge" not in kg_results:
                context_parts.append(f"Structured Knowledge:\n{kg_results}")

        # Run the agent (with optional tool use)
        if agent_name == "Researcher" and hasattr(agent, "research"):
            result = agent.research(objective)
        else:
            # Allow key agents to use tools
            if agent_name in ["Analyst", "Critic", "Writer", "Planner"]:
                result = self.tool_user.try_use_tools(agent, full_prompt)
            else:
                result = agent.think(full_prompt)

        task.complete(result)
        self.logger.log(agent_name, f"Completed: {task_title}")

        tokens_after = getattr(agent, "total_tokens_estimated", 0)
        tokens_used = max(0, tokens_after - tokens_before)

        # Record step in RunState
        if run_state:
            step_num = len(run_state.steps) + 1
            run_state.add_step(step_num, agent_name, task_title, prompt, result, tokens_est=tokens_used)
            run_state.save()

        # Send result notification across MessageBus
        self.message_bus.send(
            sender=agent_name,
            receiver="ALL",
            content=f"Finished '{task_title}'. Summary: {result[:120]}...",
            msg_type="result"
        )
        
        # Check if the agent is requesting help from another agent
        help_request = detect_help_request(result)
        if help_request:
            target_agent, reason = help_request
            if target_agent != agent_name and target_agent in self.agents.list_agents():
                help_result = self._request_help(agent_name, target_agent, result, objective)
                result = result + f"\n\n=== Help from {target_agent} ===\n{help_result}"

        print(f"\n{agent_name} output ({tokens_used} est. tokens):")
        print(result[:1200] + ("..." if len(result) > 1200 else ""))
        print("-" * 50)

        return result

    def run(self, objective: str, project_id: str = None, continue_from_run: str = None, max_steps: int = 15) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print(f"🧠 MAA {Settings.VERSION} (Autonomous Dynamic Mesh)")
        print("=" * 60)
        print(f"Objective: {objective}\n")

        previous_context = ""
        if continue_from_run:
            previous = self.memory.load_run(continue_from_run)
            if previous:
                print(f"🔄 Continuing from previous run: {continue_from_run}")
                previous_context = f"""
Previous Run Context:
Objective: {previous.get('objective')}
Final Answer: {previous.get('final', '')[:1000]}
Verification: {previous.get('verification', '')[:500]}
"""
                print(previous_context[:400] + "...")
                print("-" * 50)
        self.logger.start_run(objective)
        run_state = RunState(objective=objective, project_id=project_id)

        # Project Context
        if project_id:
            project = self.project_manager.get_project(project_id)
            if project:
                print(f"📁 Project Context Loaded: {project.name}")

        coordinator = self.agents.get("Coordinator")

        # Dynamic loop execution without artificial inhibitors
        step_count = 0

        while step_count < max_steps:
            step_count += 1

            decision = coordinator.decide_next_action(
                objective=objective,
                steps_taken=run_state.steps,
                message_history=self.message_bus.to_list()
            )

            status = decision.get("status", "CONTINUE")
            next_agent = decision.get("next_agent", "Researcher")
            task_title = decision.get("task_title", f"Dynamic Step {step_count}")
            instructions = decision.get("instructions", objective)

            if status == "COMPLETE" or (next_agent == "Coordinator" and step_count > 1):
                print("\n🎯 Coordinator concluded the dynamic execution mesh.")
                break

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
        
        print("\n→ Evaluating execution quality...")
        evaluation = self.evaluator.evaluate(objective, final_summary, verification)
        score = evaluation.get("score", 8.0)
        print(f"   Quality Score: {score}/10")

        run_state.mark_completed(final_summary, quality_score=score)
        run_state.save()

        # Build telemetry results
        results = {
            "run_id": run_state.run_id,
            "objective": objective,
            "final": final_summary,
            "verification": verification,
            "evaluation": evaluation,
            "total_steps": len(run_state.steps),
            "total_tokens_estimated": run_state.total_tokens_estimated,
            "steps": run_state.steps,
            "messages": run_state.messages,
            "tasks": self.task_manager.get_all_tasks()
        }
        
        # Extract simple knowledge from the final answer
        if self.knowledge_graph and results.get("final"):
            try:
                # Very simple extraction for now
                final_text = results["final"]
                # Add a general claim from this run
                self.knowledge_graph.add_entity("Current Research", "topic")
                self.knowledge_graph.add_claim(
                    subject="Current Research",
                    claim=final_text[:300],
                    source_run=results.get("evaluation", {}).get("score", "unknown"),
                    confidence=0.6
                )
                print("知识已添加到 Knowledge Graph")
            except Exception as e:
                print(f"⚠️ Could not update knowledge graph: {e}")

        self.memory.save_run(objective, results)
        if project_id:
            self.project_manager.add_run_to_project(project_id, run_state.run_id)

        self.logger.end_run(score)
        print(f"\n⚡ Total Steps Executed: {len(run_state.steps)} | Total Estimated Tokens: {run_state.total_tokens_estimated}")
        print("\n" + self.task_manager.summary())
        return results

    def resume_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        run_state = RunState.load(run_id)
        if not run_state:
            print(f"Error: Run state '{run_id}' not found.")
            return None

        print(f"\n🔄 Resuming run {run_id} for objective: {run_state.objective}")
        return self.run(run_state.objective, project_id=run_state.project_id)
    
    def _request_help(self, from_agent: str, to_agent: str, context: str, objective: str) -> str:
        """Allow one agent to request help from another."""
        print(f"\n🤝 {from_agent} is requesting help from {to_agent}...")

        help_prompt = f"""Another agent ({from_agent}) is requesting your help.

    Original Objective: {objective}

    Context from {from_agent}:
    {context[:1200]}

    Please provide specialized help according to your role.
    """

        return self._run_agent(
            agent_name=to_agent,
            prompt=help_prompt,
            task_title=f"Help request from {from_agent}",
            objective=objective,
            use_memory=False
        )