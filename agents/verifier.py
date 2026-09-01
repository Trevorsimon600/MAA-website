from core.agent import Agent

class Verifier(Agent):
    def __init__(self, tool_registry=None):
        super().__init__(
            name="Verifier",
            role="Quality Verifier",
            instructions="""You are the Verifier of MAA.

Your job is to check whether the final answer fully meets the original objective.

You must answer these questions clearly:
1. Does the final answer address the original objective?
2. Are the main points supported by the research?
3. Did the Critic's concerns get properly considered?
4. What is still missing or weak?
5. Overall quality score (1-10) with a short justification.

Be strict but fair. Always give a clear final judgment.""",
            tool_registry=tool_registry
        )