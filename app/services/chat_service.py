import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Generator, Dict, Union
from app.database.repository import ChatRepository
from app.database.models import Conversation, Message, AppSettings
from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.services.title_service import TitleService
from app.core.logger import logger
from app.core.exceptions import LocalAIException

class ChatService:
    """Core service managing chat sessions, database operations, context windows, and attachments."""

    def __init__(
        self,
        repository: Optional[ChatRepository] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        self.repo = repository or ChatRepository()
        self.llm = llm_provider or OllamaProvider()
        self.settings: AppSettings = self.repo.load_app_settings()

    def reload_settings(self) -> AppSettings:
        """Reload settings from repository."""
        self.settings = self.repo.load_app_settings()
        return self.settings

    def create_new_conversation(self, model_name: str = "") -> Conversation:
        """Create a new conversation with a unique UUID."""
        selected_model = model_name or self.settings.default_model or "qwen2.5"
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        conv = Conversation(
            id=conv_id,
            title="New Chat",
            created_at=now,
            updated_at=now,
            model=selected_model,
            messages=[]
        )
        return self.repo.create_conversation(conv)

    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation with messages."""
        return self.repo.get_conversation(conversation_id, load_messages=True)

    def list_conversations(self) -> List[Conversation]:
        """List all conversations sorted by updated_at desc."""
        return self.repo.list_conversations()

    def search_conversations(self, query: str) -> List[Conversation]:
        """Search conversations by title or message text."""
        return self.repo.search_conversations(query)

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation by ID."""
        return self.repo.delete_conversation(conversation_id)

    def delete_all_conversations(self) -> bool:
        """Delete all conversations."""
        return self.repo.delete_all_conversations()

    def parse_file_attachment(self, file_path: Union[str, Path]) -> str:
        """Read and format text contents of attached files (.txt, .md, .csv, .json)."""
        path = Path(file_path)
        if not path.exists():
            raise LocalAIException(f"Attachment file not found: {path}")

        valid_exts = {".txt", ".md", ".csv", ".json", ".py", ".html", ".css", ".js"}
        if path.suffix.lower() not in valid_exts:
            raise LocalAIException(f"Unsupported file format '{path.suffix}'. Supported: {', '.join(valid_exts)}")

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            return f"\n\n[Attached File: {path.name}]\n```\n{content}\n```\n"
        except Exception as e:
            logger.error(f"Failed to read attachment file {path}: {e}")
            raise LocalAIException(f"Could not read attached file: {e}")

    def prepare_context_messages(self, conversation: Conversation, max_messages: int = 20) -> List[Dict[str, str]]:
        """Trim long conversation history to fit context window safely."""
        msgs = conversation.messages
        if len(msgs) > max_messages:
            # Keep system messages if any, and last N messages
            system_msgs = [m for m in msgs if m.role == "system"]
            user_assistant_msgs = [m for m in msgs if m.role in ("user", "assistant")]
            recent_msgs = user_assistant_msgs[-max_messages:]
            msgs = system_msgs + recent_msgs

        return [{"role": m.role, "content": m.content} for m in msgs]

    def send_message_stream(
        self,
        conversation_id: str,
        user_content: str,
        model_name: str,
        attachment_path: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Add user message, auto-title if needed, and stream assistant tokens."""
        conv = self.repo.get_conversation(conversation_id, load_messages=True)
        if not conv:
            conv = self.create_new_conversation(model_name=model_name)
            conversation_id = conv.id

        full_user_content = user_content
        if attachment_path:
            attach_text = self.parse_file_attachment(attachment_path)
            full_user_content += attach_text

        # Add user message to DB
        now = datetime.now().isoformat()
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=full_user_content,
            timestamp=now
        )
        self.repo.add_message(user_msg)
        conv.messages.append(user_msg)

        # Auto title generation on first user message
        if conv.title == "New Chat" or len([m for m in conv.messages if m.role == "user"]) == 1:
            auto_title = TitleService.generate_title_from_text(user_content)
            self.repo.update_conversation_title(conversation_id, auto_title)
            conv.title = auto_title

        # Ensure model is updated on conversation
        if model_name and conv.model != model_name:
            self.repo.update_conversation_model(conversation_id, model_name)
            conv.model = model_name

        # Prepare context window
        context_msgs = self.prepare_context_messages(conv)

        # Stream response tokens
        accumulated_response = []
        try:
            for token in self.llm.stream(
                messages=context_msgs,
                model=model_name or conv.model,
                system_prompt=self.settings.system_prompt,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            ):
                accumulated_response.append(token)
                yield token

        finally:
            # Save complete assistant message to DB
            full_reply = "".join(accumulated_response)
            if full_reply.strip():
                assistant_msg = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=full_reply,
                    timestamp=datetime.now().isoformat()
                )
                self.repo.add_message(assistant_msg)
