import os
from dotenv import load_dotenv

# Load local .env file when running MAA locally
load_dotenv()


def get_secret(name: str, default: str = "") -> str:
    """
    Get configuration from:
    1. Environment variables / local .env
    2. Streamlit Secrets
    """

    # First try environment variables
    value = os.getenv(name)

    if value:
        return value

    # Then try Streamlit Secrets
    try:
        import streamlit as st

        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return default


class Settings:
    """Central configuration for MAA v0.2"""

    # API Keys
    GROQ_API_KEY: str = get_secret("GROQ_API_KEY")
    OPENAI_API_KEY: str = get_secret("OPENAI_API_KEY")

    # Model settings - Verified available Groq models
    DEFAULT_MODEL: str = get_secret(
        "DEFAULT_MODEL",
        "openai/gpt-oss-20b"
    )

    FALLBACK_MODELS: list = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b"
    ]

    TEMPERATURE: float = float(
        get_secret("TEMPERATURE", "0.3")
    )

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
        """
        Ensure at least one AI provider is configured.
        """

        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError(
                "No AI API key configured. "
                "Add GROQ_API_KEY or OPENAI_API_KEY "
                "to .env or Streamlit Secrets."
            )

        print(f"MAA {cls.VERSION} | Config loaded successfully")