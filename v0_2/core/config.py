import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Central configuration for MAA v0.2"""

    # API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai/gpt-oss-20b")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

    # System
    VERSION: str = "0.2.0-dev"
    MAX_TOOL_STEPS: int = 5
    MAX_MEMORY_ENTRIES: int = 60

    # Paths
    RUNS_DIR: str = "runs"
    KNOWLEDGE_FILE: str = "knowledge_base.json"
    PROJECTS_FILE: str = "projects.json"

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")
        print(f"✅ MAA {cls.VERSION} | Config loaded successfully")