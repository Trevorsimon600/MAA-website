import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

class KnowledgeGraph:
    """
    Simple file-based knowledge graph for MAA.
    Stores entities, claims, and relationships.
    """

    def __init__(self, storage_file: str = "knowledge_graph.json"):
        self.storage_file = storage_file
        self.data = {
            "entities": {},
            "claims": [],
            "relationships": []
        }
        self._load()

    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def _save(self):
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_entity(self, name: str, entity_type: str = "concept", description: str = "") -> str:
        entity_id = name.lower().replace(" ", "_")
        if entity_id not in self.data["entities"]:
            self.data["entities"][entity_id] = {
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            self._save()
        return entity_id

    def add_claim(self, subject: str, claim: str, source_run: str = "", confidence: float = 0.7) -> str:
        claim_id = str(uuid.uuid4())[:8]
        entry = {
            "id": claim_id,
            "subject": subject.lower().replace(" ", "_"),
            "claim": claim,
            "source_run": source_run,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        }
        self.data["claims"].append(entry)
        self._save()
        return claim_id

    def add_relationship(self, from_entity: str, to_entity: str, relation: str):
        rel = {
            "from": from_entity.lower().replace(" ", "_"),
            "to": to_entity.lower().replace(" ", "_"),
            "relation": relation,
            "created_at": datetime.now().isoformat()
        }
        self.data["relationships"].append(rel)
        self._save()

    def get_entity_claims(self, entity_name: str) -> List[Dict]:
        entity_id = entity_name.lower().replace(" ", "_")
        return [c for c in self.data["claims"] if c["subject"] == entity_id]

    def search(self, query: str, max_results: int = 6) -> str:
        query = query.lower()
        results = []

        # Search claims
        for claim in self.data["claims"]:
            if query in claim["claim"].lower() or query in claim["subject"]:
                results.append(f"- ({claim['subject']}) {claim['claim']}")

        # Search entities
        for eid, ent in self.data["entities"].items():
            if query in ent["name"].lower() or query in ent.get("description", "").lower():
                results.append(f"- Entity: {ent['name']} ({ent['type']})")

        if not results:
            return "No relevant knowledge found in the graph."

        return "Knowledge Graph results:\n" + "\n".join(results[:max_results])

    def summary(self) -> str:
        return (
            f"Knowledge Graph → "
            f"Entities: {len(self.data['entities'])} | "
            f"Claims: {len(self.data['claims'])} | "
            f"Relationships: {len(self.data['relationships'])}"
        )