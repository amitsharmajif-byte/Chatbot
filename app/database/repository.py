import sqlite3
import json
from contextlib import contextmanager
from typing import List, Optional, Dict
from app.database.database import Database
from app.database.models import Conversation, Message, AppSettings
from app.core.logger import logger
from app.core.exceptions import DatabaseError

class ChatRepository:
    """Repository handling SQLite persistence for conversations, messages, and settings."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    @contextmanager
    def _db_connection(self):
        conn = self.db.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    # --- Conversation CRUD ---

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """Create a new conversation record."""
        query = """
        INSERT INTO conversations (id, title, created_at, updated_at, model)
        VALUES (?, ?, ?, ?, ?);
        """
        try:
            with self._db_connection() as conn:
                conn.execute(
                    query,
                    (conversation.id, conversation.title, conversation.created_at, conversation.updated_at, conversation.model)
                )
                conn.commit()
                logger.info(f"Created conversation: {conversation.id} ('{conversation.title}')")
                return conversation
        except sqlite3.Error as e:
            logger.error(f"Error creating conversation {conversation.id}: {e}")
            raise DatabaseError(f"Could not create conversation: {e}")

    def get_conversation(self, conversation_id: str, load_messages: bool = True) -> Optional[Conversation]:
        """Fetch a conversation by ID, optionally including its messages."""
        query = "SELECT id, title, created_at, updated_at, model FROM conversations WHERE id = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (conversation_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                conv = Conversation(
                    id=row["id"],
                    title=row["title"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    model=row["model"]
                )
                if load_messages:
                    conv.messages = self.get_messages_for_conversation(conversation_id)
                return conv
        except sqlite3.Error as e:
            logger.error(f"Error fetching conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not fetch conversation: {e}")

    def list_conversations(self) -> List[Conversation]:
        """Return all conversations ordered by updated_at descending."""
        query = "SELECT id, title, created_at, updated_at, model FROM conversations ORDER BY updated_at DESC;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                conversations = []
                for row in rows:
                    conversations.append(Conversation(
                        id=row["id"],
                        title=row["title"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        model=row["model"]
                    ))
                return conversations
        except sqlite3.Error as e:
            logger.error(f"Error listing conversations: {e}")
            raise DatabaseError(f"Could not list conversations: {e}")

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update a conversation title."""
        query = "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (title, conversation_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating title for conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not update conversation title: {e}")

    def update_conversation_model(self, conversation_id: str, model: str) -> bool:
        """Update the model used for a conversation."""
        query = "UPDATE conversations SET model = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (model, conversation_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating model for conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not update conversation model: {e}")

    def update_conversation_timestamp(self, conversation_id: str, timestamp: str) -> bool:
        """Update the updated_at timestamp for a conversation."""
        query = "UPDATE conversations SET updated_at = ? WHERE id = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (timestamp, conversation_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error updating timestamp for conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not update conversation timestamp: {e}")

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        query = "DELETE FROM conversations WHERE id = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (conversation_id,))
                conn.commit()
                logger.info(f"Deleted conversation {conversation_id}")
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not delete conversation: {e}")

    def delete_all_conversations(self) -> bool:
        """Delete all conversations and messages."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages;")
                cursor.execute("DELETE FROM conversations;")
                conn.commit()
                logger.info("Deleted all conversations and messages.")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting all conversations: {e}")
            raise DatabaseError(f"Could not delete all conversations: {e}")

    def search_conversations(self, search_query: str) -> List[Conversation]:
        """Search conversations by title or message content."""
        if not search_query.strip():
            return self.list_conversations()
        
        like_term = f"%{search_query.strip()}%"
        query = """
        SELECT DISTINCT c.id, c.title, c.created_at, c.updated_at, c.model
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.title LIKE ? OR m.content LIKE ?
        ORDER BY c.updated_at DESC;
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (like_term, like_term))
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(Conversation(
                        id=row["id"],
                        title=row["title"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        model=row["model"]
                    ))
                return results
        except sqlite3.Error as e:
            logger.error(f"Error searching conversations with query '{search_query}': {e}")
            raise DatabaseError(f"Search failed: {e}")

    # --- Message CRUD ---

    def add_message(self, message: Message) -> Message:
        """Add a message to a conversation and touch conversation updated_at."""
        query = """
        INSERT INTO messages (conversation_id, role, content, timestamp)
        VALUES (?, ?, ?, ?);
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (message.conversation_id, message.role, message.content, message.timestamp))
                message.id = cursor.lastrowid
                
                # Touch conversation updated_at
                conn.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?;",
                    (message.timestamp, message.conversation_id)
                )
                conn.commit()
                return message
        except sqlite3.Error as e:
            logger.error(f"Error adding message to conversation {message.conversation_id}: {e}")
            raise DatabaseError(f"Could not add message: {e}")

    def get_messages_for_conversation(self, conversation_id: str) -> List[Message]:
        """Fetch all messages for a specific conversation in chronological order."""
        query = """
        SELECT id, conversation_id, role, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC;
        """
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (conversation_id,))
                rows = cursor.fetchall()
                messages = []
                for row in rows:
                    messages.append(Message(
                        id=row["id"],
                        conversation_id=row["conversation_id"],
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"]
                    ))
                return messages
        except sqlite3.Error as e:
            logger.error(f"Error fetching messages for conversation {conversation_id}: {e}")
            raise DatabaseError(f"Could not fetch messages: {e}")

    # --- Settings Storage ---

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a setting string value by key."""
        query = "SELECT value FROM settings WHERE key = ?;"
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (key,))
                row = cursor.fetchone()
                return row["value"] if row else default
        except sqlite3.Error as e:
            logger.error(f"Error getting setting '{key}': {e}")
            return default

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting key-value pair."""
        query = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);"
        try:
            with self._db_connection() as conn:
                conn.execute(query, (key, value))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error setting '{key}' = '{value}': {e}")
            raise DatabaseError(f"Could not save setting: {e}")

    def load_app_settings(self) -> AppSettings:
        """Load AppSettings object from database or return defaults."""
        defaults = AppSettings()
        try:
            settings_str = self.get_setting("app_settings", "")
            if settings_str:
                data = json.loads(settings_str)
                return AppSettings(**data)
        except Exception as e:
            logger.warning(f"Failed to parse saved settings, returning defaults: {e}")
        return defaults

    def save_app_settings(self, settings: AppSettings) -> bool:
        """Save AppSettings object to database."""
        try:
            data = {
                "provider": settings.provider,
                "ollama_host": settings.ollama_host,
                "huggingface_api_key": settings.huggingface_api_key,
                "default_model": settings.default_model,
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens,
                "system_prompt": settings.system_prompt,
                "theme": settings.theme,
                "streaming_enabled": settings.streaming_enabled,
                "enter_to_send": settings.enter_to_send,
                "show_timestamps": settings.show_timestamps,
                "auto_save": settings.auto_save,
            }
            return self.set_setting("app_settings", json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to save app settings: {e}")
            raise DatabaseError(f"Could not save settings: {e}")
