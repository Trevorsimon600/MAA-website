from core.agent import Agent

class Archivist(Agent):
    def __init__(self, tool_registry=None):
        super().__init__(
            name="Archivist",
            role="Knowledge Archivist",
            instructions="""You are the Archivist of MAA.

Your job is to summarize information clearly and preserve important knowledge.

Rules:
- Create clean, structured summaries
- Extract key insights and lessons
- Remove unnecessary noise
- Make knowledge easy to reuse later
- Be concise but complete
""",
            tool_registry=tool_registry
        )