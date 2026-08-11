import sqlite3
from pathlib import Path
from typing import Union
from app.core.config import DB_PATH, DATA_DIR
from app.core.logger import logger
from app.core.exceptions import DatabaseError

class Database:
    """SQLite Database connection and schema initializer."""

    def __init__(self, db_path: Union[str, Path] = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Return SQLite connection with Row factory enabled."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database at {self.db_path}: {e}")
            raise DatabaseError(f"Database connection error: {e}")

    def init_db(self):
        """Initialize database tables and indexes if they do not exist."""
        create_conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            model TEXT NOT NULL
        );
        """

        create_messages_table = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
        );
        """

        create_settings_table = """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """

        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
        """

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(create_conversations_table)
            cursor.execute(create_messages_table)
            cursor.execute(create_settings_table)
            cursor.executescript(create_indexes)
            conn.commit()
            logger.info(f"Database initialized successfully at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")
        finally:
            if conn:
                conn.close()

