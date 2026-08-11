import tempfile
import unittest
from pathlib import Path
from app.services.title_service import TitleService
from app.services.export_service import ExportService
from app.database.models import Conversation, Message

class TestChatServices(unittest.TestCase):

    def test_title_service_generation(self):
        title1 = TitleService.generate_title_from_text("Explain machine learning in simple terms")
        self.assertEqual(title1, "Explain machine learning in simple terms")

        long_prompt = "Can you help me write a complex Python script to parse CSV files and generate daily summary reports for logistics?"
        title2 = TitleService.generate_title_from_text(long_prompt, max_words=6)
        self.assertEqual(title2, "Can you help me write a...")

        code_prompt = "```python\nprint('hello')\n```"
        title3 = TitleService.generate_title_from_text(code_prompt)
        self.assertEqual(title3, "New Chat")

    def test_export_service(self):
        temp_dir = tempfile.TemporaryDirectory()
        try:
            conv = Conversation(
                id="exp-1",
                title="Export Sample",
                created_at="2026-08-11T10:00:00",
                model="qwen2.5",
                messages=[
                    Message(role="user", content="Hello AI", timestamp="10:00:01"),
                    Message(role="assistant", content="Hello User!", timestamp="10:00:03")
                ]
            )

            # Test Markdown Export
            md_path = Path(temp_dir.name) / "test.md"
            ExportService.export_to_markdown(conv, md_path)
            self.assertTrue(md_path.exists())
            md_text = md_path.read_text(encoding="utf-8")
            self.assertIn("# Export Sample", md_text)
            self.assertIn("Hello AI", md_text)

            # Test Text Export
            txt_path = Path(temp_dir.name) / "test.txt"
            ExportService.export_to_txt(conv, txt_path)
            self.assertTrue(txt_path.exists())
            txt_text = txt_path.read_text(encoding="utf-8")
            self.assertIn("TITLE: Export Sample", txt_text)

            # Test JSON Export
            json_path = Path(temp_dir.name) / "test.json"
            ExportService.export_to_json(conv, json_path)
            self.assertTrue(json_path.exists())
            json_text = json_path.read_text(encoding="utf-8")
            self.assertIn('"id": "exp-1"', json_text)

        finally:
            temp_dir.cleanup()

if __name__ == "__main__":
    unittest.main()
