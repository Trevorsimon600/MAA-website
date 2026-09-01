import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from v0_2 import MAA

if __name__ == "__main__":
    objective = "Explain the main advantages and risks of multi-agent AI systems compared to single powerful models."
    
    print("🚀 Initializing MAA CLI Execution...")
    maa = MAA()
    maa.run(objective)