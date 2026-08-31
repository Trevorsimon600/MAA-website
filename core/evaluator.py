from agents.verifier import Verifier
from typing import Dict, Any

class Evaluator:
    def __init__(self):
        self.verifier = Verifier()

    def evaluate(self, objective: str, final_answer: str, verification: str = "") -> Dict[str, Any]:
        """
        Produce a simple quality score and short judgment.
        """
        prompt = f"""You are evaluating the quality of an AI system's final answer.

Original Objective:
{objective}

Final Answer:
{final_answer}

Verifier comments:
{verification[:800] if verification else "None"}

Give your evaluation in this exact format:

Score: <number from 1 to 10>
Judgment: <one short paragraph>
Strengths: <bullet points>
Weaknesses: <bullet points>
"""

        result = self.verifier.think(prompt)

        # Try to extract the score
        score = 5  # default
        try:
            for line in result.splitlines():
                if line.strip().lower().startswith("score:"):
                    number = ''.join(c for c in line if c.isdigit())
                    if number:
                        score = int(number)
                        score = max(1, min(10, score))
                        break
        except Exception:
            pass

        return {
            "score": score,
            "full_evaluation": result
        }