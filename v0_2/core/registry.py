from typing import Dict, Type
from core.agent import Agent

class AgentRegistry:
    """Registry to manage all available agents."""

    def __init__(self):
        self._agents: Dict[str, Agent] = {}

    def register(self, name: str, agent: Agent):
        self._agents[name] = agent

    def get(self, name: str) -> Agent:
        agent = self._agents.get(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found in registry.")
        return agent

    def list_agents(self) -> list:
        return list(self._agents.keys())

    def all(self) -> Dict[str, Agent]:
        return self._agents