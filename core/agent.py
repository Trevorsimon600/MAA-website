# At the top of core/agent.py add:
from v0_2.core.model_router import ModelRouter
from v0_2.core.config import Settings

class Agent:
    def __init__(self, name: str, role: str, instructions: str, provider: str = "groq"):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.router = ModelRouter(provider=provider)

    def think(self, prompt: str, max_retries: int = 2) -> str:
        system_prompt = f"""You are {self.name}, the {self.role}.

{self.instructions}

Always respond helpfully and clearly."""

        for attempt in range(max_retries + 1):
            result = self.router.chat(
                system_prompt=system_prompt,
                user_prompt=prompt,
                temperature=Settings.TEMPERATURE
            )
            if result and not result.startswith("Error from"):
                return result
            if attempt < max_retries:
                print(f"   ⚠️  Retry {attempt + 1} for {self.name}...")
        
        return result or f"[{self.name}] No response generated."