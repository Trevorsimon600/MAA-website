from datetime import datetime
from typing import List, Dict, Any
import json
import os

class MAALogger:
    """Simple observability logger for MAA v0.2."""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.current_run: List[Dict[str, Any]] = []
        self.run_id = None

    def start_run(self, objective: str):
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_run = []
        self.log("SYSTEM", f"Run started | Objective: {objective}")

    def log(self, agent: str, message: str, level: str = "INFO"):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "level": level,
            "message": message
        }
        self.current_run.append(entry)
        
        # Print to console in a clean way
        time_str = entry["timestamp"][11:19]
        print(f"[{time_str}] {agent:<12} | {message}")

    def log_tool(self, agent: str, tool_name: str, tool_input: str):
        self.log(agent, f"Tool used: {tool_name} → {tool_input[:60]}...", level="TOOL")

    def log_score(self, score: int):
        self.log("EVALUATOR", f"Quality Score: {score}/10", level="SCORE")

    def end_run(self, final_score: int = None):
        if final_score is not None:
            self.log_score(final_score)
        
        self.log("SYSTEM", "Run finished")

        # Save log to file
        if self.run_id:
            filepath = os.path.join(self.log_dir, f"log_{self.run_id}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.current_run, f, indent=2, ensure_ascii=False)
            print(f"\n📝 Log saved: {filepath}")

    def get_summary(self) -> str:
        lines = []
        for entry in self.current_run:
            lines.append(f"{entry['timestamp'][11:19]} | {entry['agent']}: {entry['message']}")
        return "\n".join(lines)