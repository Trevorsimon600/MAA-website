from typing import List, Dict, Optional
from datetime import datetime
import uuid

class Message:
    def __init__(self, sender: str, receiver: str, content: str, msg_type: str = "info"):
        self.id = str(uuid.uuid4())[:8]
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.msg_type = msg_type          # info | request_help | result | challenge | handoff | warning
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.msg_type,
            "timestamp": self.timestamp
        }

    def __str__(self):
        return f"[{self.timestamp[11:19]}] [{self.msg_type.upper()}] {self.sender} → {self.receiver}: {self.content[:80]}"


class MessageBus:
    def __init__(self):
        self.messages: List[Message] = []

    def send(self, sender: str, receiver: str, content: str, msg_type: str = "info") -> Message:
        msg = Message(sender, receiver, content, msg_type)
        self.messages.append(msg)
        print(f"   📨 [{msg_type.upper()}] {sender} → {receiver}: {content[:60]}...")
        return msg

    def request_help(self, sender: str, target: str, topic: str) -> Message:
        """Helper for an agent to formally request assistance from another agent."""
        return self.send(
            sender=sender,
            receiver=target,
            content=f"HELP REQUEST: I need assistance with '{topic}'.",
            msg_type="request_help"
        )

    def get_messages_for(self, agent_name: str) -> List[Message]:
        return [m for m in self.messages if m.receiver == agent_name or m.receiver == "ALL"]

    def get_pending_help_requests(self) -> List[Message]:
        return [m for m in self.messages if m.msg_type == "request_help"]

    def get_conversation(self) -> List[str]:
        return [str(m) for m in self.messages]

    def to_list(self) -> List[dict]:
        return [m.to_dict() for m in self.messages]

    def clear(self):
        self.messages = []