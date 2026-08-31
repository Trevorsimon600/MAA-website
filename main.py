from core.config import Config
from core.orchestrator import Orchestrator


if __name__ == "__main__":
    Config.validate()

    # You can change this objective anytime
    objective = "Explain the main advantages and risks of multi-agent AI systems compared to single powerful models."

    orchestrator = Orchestrator()
    orchestrator.run(objective)