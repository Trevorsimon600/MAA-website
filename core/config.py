import os
from dotenv import load_dotenv

# Load variables from .env when running locally
load_dotenv()


def get_secret(name):
    """
    Get a secret from the environment first.
    If it is not available, try Streamlit Secrets.
    """

    # Local environment / .env
    value = os.getenv(name)

    if value:
        return value

    # Streamlit Cloud
    try:
        import streamlit as st

        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return None


class Settings:
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

    @classmethod
    def validate(cls):
        """
        Make sure at least one AI provider is configured.
        """

        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError(
                "No AI API key configured. "
                "Add GROQ_API_KEY or OPENAI_API_KEY "
                "to .env or Streamlit Secrets."
            )

# Alias Config for backwards compatibility
Config = Settings