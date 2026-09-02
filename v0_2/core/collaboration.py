import re
from typing import Optional, Tuple

def detect_help_request(text: str) -> Optional[Tuple[str, str]]:
    """
    Detect if an agent is requesting help from another agent.
    Returns (agent_name, reason) or None.
    """
    # Pattern examples:
    # "I need help from the Analyst"
    # "Requesting assistance from Writer"
    # "Please ask the Critic to review this"
    
    patterns = [
        r"(?:need help from|requesting help from|ask the|consult the|call the)\s+(Coordinator|Planner|Researcher|Analyst|Writer|Critic|Verifier|Archivist)",
        r"(Coordinator|Planner|Researcher|Analyst|Writer|Critic|Verifier|Archivist)\s+should\s+(?:handle|review|analyze|write|check)",
    ]

    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            agent_name = match.group(1).capitalize()
            # Normalize names
            name_map = {
                "Coordinator": "Coordinator",
                "Planner": "Planner",
                "Researcher": "Researcher",
                "Analyst": "Analyst",
                "Writer": "Writer",
                "Critic": "Critic",
                "Verifier": "Verifier",
                "Archivist": "Archivist"
            }
            agent_name = name_map.get(agent_name, agent_name)
            return agent_name, text
    
    return None