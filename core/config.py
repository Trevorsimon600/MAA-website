import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    DEFAULT_MODEL = "openai/gpt-oss-20b"  # Good free model on open ai
    MAX_STEPS = 8
    TEMPERATURE = 0.3

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing in .env file")
        print("✅ Config loaded successfully")