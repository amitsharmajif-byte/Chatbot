from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Message:
    id: Optional[int] = None
    conversation_id: str = ""
    role: str = "user"  # system, user, assistant
    content: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

@dataclass
class Conversation:
    id: str = ""
    title: str = "New Chat"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    model: str = ""
    messages: List[Message] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
            "messages": [m.to_dict() for m in self.messages]
        }

@dataclass
class AppSettings:
    provider: str = "ollama"  # ollama, huggingface
    ollama_host: str = "http://localhost:11434"
    huggingface_api_key: str = ""
    default_model: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = "You are a helpful, respectful, and honest AI assistant."
    theme: str = "dark"
    streaming_enabled: bool = True
    enter_to_send: bool = True
    show_timestamps: bool = True
    auto_save: bool = True
