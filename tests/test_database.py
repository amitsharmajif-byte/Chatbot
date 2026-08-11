import tempfile
import unittest
from pathlib import Path
from app.database.database import Database
from app.database.repository import ChatRepository
from app.database.models import Conversation, Message, AppSettings

class TestDatabaseRepository(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_chatbot.db"
        self.db = Database(db_path=self.db_path)
        self.repo = ChatRepository(db=self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_get_conversation(self):
        conv = Conversation(
            id="test-conv-1",
            title="Test Chat",
            created_at="2026-08-11T12:00:00",
            updated_at="2026-08-11T12:00:00",
            model="qwen2.5"
        )
        self.repo.create_conversation(conv)

        fetched = self.repo.get_conversation("test-conv-1")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Test Chat")
        self.assertEqual(fetched.model, "qwen2.5")

    def test_messages_crud(self):
        conv = Conversation(id="conv-msg-1", title="Message Test", model="llama3.2")
        self.repo.create_conversation(conv)

        msg1 = Message(conversation_id="conv-msg-1", role="user", content="Hello world")
        msg2 = Message(conversation_id="conv-msg-1", role="assistant", content="Hi there!")

        self.repo.add_message(msg1)
        self.repo.add_message(msg2)

        messages = self.repo.get_messages_for_conversation("conv-msg-1")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].role, "user")
        self.assertEqual(messages[0].content, "Hello world")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[1].content, "Hi there!")

    def test_search_conversations(self):
        conv1 = Conversation(id="c1", title="Python Data Analysis", model="qwen")
        conv2 = Conversation(id="c2", title="Machine Learning Basics", model="qwen")
        self.repo.create_conversation(conv1)
        self.repo.create_conversation(conv2)

        self.repo.add_message(Message(conversation_id="c1", role="user", content="How to use pandas?"))
        self.repo.add_message(Message(conversation_id="c2", role="user", content="Explain neural networks"))

        res_title = self.repo.search_conversations("Python")
        self.assertEqual(len(res_title), 1)
        self.assertEqual(res_title[0].id, "c1")

        res_msg = self.repo.search_conversations("pandas")
        self.assertEqual(len(res_msg), 1)
        self.assertEqual(res_msg[0].id, "c1")

    def test_delete_conversation(self):
        conv = Conversation(id="c-del", title="To Delete")
        self.repo.create_conversation(conv)
        self.repo.add_message(Message(conversation_id="c-del", role="user", content="test"))

        deleted = self.repo.delete_conversation("c-del")
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get_conversation("c-del"))

    def test_settings_storage(self):
        settings = AppSettings(
            default_model="qwen2.5",
            temperature=0.8,
            theme="light"
        )
        self.repo.save_app_settings(settings)

        loaded = self.repo.load_app_settings()
        self.assertEqual(loaded.default_model, "qwen2.5")
        self.assertEqual(loaded.temperature, 0.8)
        self.assertEqual(loaded.theme, "light")

if __name__ == "__main__":
    unittest.main()
