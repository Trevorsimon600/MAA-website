import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class SimpleMemory:
    def __init__(self, storage_dir: str = "runs", knowledge_file: str = "knowledge_base.json"):
        self.storage_dir = storage_dir
        self.knowledge_file = knowledge_file
        os.makedirs(self.storage_dir, exist_ok=True)

        # Create knowledge base if it doesn't exist
        if not os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump({"entries": []}, f, indent=2)

    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load and return all entries from the knowledge base file."""
        try:
            if not os.path.exists(self.knowledge_file):
                return []
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                kb = json.load(f)
            return kb.get("entries", [])
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []

    def save_run(self, objective: str, results: Dict[str, Any]) -> str:
        """Save a complete MAA run + extract key knowledge."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"run_{timestamp}"

        run_data = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "objective": objective,
            "plan": results.get("plan"),
            "research": results.get("research"),
            "critique": results.get("critique"),
            "final": results.get("final"),
            "verification": results.get("verification"),
            "evaluation": results.get("evaluation"),
            "tasks_summary": [
                {
                    "id": getattr(t, "id", None),
                    "title": getattr(t, "title", None),
                    "status": t.status.value if hasattr(t, "status") else str(t),
                    "assigned_to": getattr(t, "assigned_to", None)
                }
                for t in results.get("tasks", [])
            ]
        }

        # Save full run
        filepath = os.path.join(self.storage_dir, f"{run_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)

        # Extract and save key knowledge
        self._add_to_knowledge_base(objective, results.get("final", ""))

        print(f"\n💾 Run saved to memory: {filepath}")
        return run_id
    
    def _extract_keywords(self, text: str) -> list:
        """Very simple keyword extraction."""
        words = text.lower().split()
        stopwords = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "what", "when", "your", "into", "about"}
        keywords = [w.strip(".,()[]") for w in words if len(w) > 4 and w not in stopwords]
        return list(dict.fromkeys(keywords))[:8]

    def _add_to_knowledge_base(self, objective: str, final_answer: str):
        """Store a clean summary of important findings."""
        try:
            kb_entries = self.load_knowledge_base()

            summary = final_answer[:500].strip() if final_answer else "No summary available"
            summary = " ".join(summary.split())

            entry = {
                "timestamp": datetime.now().isoformat(),
                "objective": objective[:120].strip(),
                "summary": summary,
                "keywords": self._extract_keywords(objective + " " + summary)
            }

            kb_entries.append(entry)
            kb_entries = kb_entries[-60:]  # Keep last 60 entries

            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump({"entries": kb_entries}, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️  Could not update knowledge base: {e}")

    def list_runs(self) -> List[str]:
        files = [f for f in os.listdir(self.storage_dir) if f.endswith(".json")]
        return sorted(files, reverse=True)

    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        if not run_id.endswith(".json"):
            run_id = f"{run_id}.json"
        filepath = os.path.join(self.storage_dir, run_id)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_latest_run(self) -> Optional[Dict[str, Any]]:
        runs = self.list_runs()
        if not runs:
            return None
        return self.load_run(runs[0])

    def search_runs(self, keyword: str) -> List[Dict[str, Any]]:
        keyword = keyword.lower()
        matches = []
        for run_file in self.list_runs():
            data = self.load_run(run_file)
            if not data:
                continue
            objective = (data.get("objective") or "").lower()
            final = (data.get("final") or "").lower()
            if keyword in objective or keyword in final:
                matches.append(data)
        return matches

    def get_memory_summary(self, max_runs: int = 5) -> str:
        """Return a short summary of recent runs."""
        runs = self.list_runs()[:max_runs]
        if not runs:
            return "No previous runs in memory."

        summary_lines = ["Recent MAA runs:"]
        for run_file in runs:
            data = self.load_run(run_file)
            if data:
                obj = data.get("objective", "Unknown")[:90]
                summary_lines.append(f"- {data.get('run_id')}: {obj}")
        return "\n".join(summary_lines)

    def get_knowledge_summary(self, max_entries: int = 6) -> str:
        """Return recent knowledge base entries in a clean format."""
        entries = self.load_knowledge_base()[-max_entries:]
        if not entries:
            return "Knowledge base is empty."

        lines = ["Relevant knowledge from previous MAA work:"]
        for e in reversed(entries):
            obj = e.get("objective", "Unknown")
            summary = e.get("summary", "")[:180]
            lines.append(f"- {obj}\n  → {summary}...")
        return "\n".join(lines)
        
    def retrieve_relevant_knowledge(self, query: str, max_results: int = 4) -> str:
        """Retrieve knowledge entries related to a query (simple keyword matching)."""
        try:
            entries = self.load_knowledge_base()
            query_words = set(query.lower().split())
            scored = []

            for entry in entries:
                text = (entry.get("objective", "") + " " + entry.get("summary", "")).lower()
                score = sum(1 for word in query_words if word in text)
                if score > 0:
                    scored.append((score, entry))

            scored.sort(reverse=True, key=lambda x: x[0])
            top = scored[:max_results]

            if not top:
                return "No highly relevant past knowledge found."

            lines = ["Retrieved relevant past knowledge:"]
            for score, entry in top:
                lines.append(f"- {entry.get('objective', '')}\n  {entry.get('summary', '')[:220]}")
            return "\n".join(lines)

        except Exception as e:
            return f"Knowledge retrieval error: {e}"