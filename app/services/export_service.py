import json
from pathlib import Path
from typing import Union
from app.database.models import Conversation
from app.core.exceptions import ExportError
from app.core.logger import logger

class ExportService:
    """Service for exporting conversations to Markdown, Text, or JSON formats."""

    @staticmethod
    def export_to_markdown(conversation: Conversation, file_path: Union[str, Path]) -> str:
        """Export conversation as a formatted Markdown file."""
        try:
            path = Path(file_path)
            lines = [
                f"# {conversation.title}",
                f"**Date:** {conversation.created_at}",
                f"**Model:** {conversation.model or 'Unknown'}",
                "---",
                ""
            ]

            for msg in conversation.messages:
                role_name = "User" if msg.role == "user" else "Assistant" if msg.role == "assistant" else "System"
                lines.append(f"### {role_name} ({msg.timestamp}):")
                lines.append(msg.content)
                lines.append("")

            content = "\n".join(lines)
            path.write_text(content, encoding="utf-8")
            logger.info(f"Exported conversation {conversation.id} to Markdown: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Failed to export conversation to Markdown: {e}")
            raise ExportError(f"Export to Markdown failed: {e}")

    @staticmethod
    def export_to_txt(conversation: Conversation, file_path: Union[str, Path]) -> str:
        """Export conversation as plain text file."""
        try:
            path = Path(file_path)
            lines = [
                f"TITLE: {conversation.title}",
                f"DATE: {conversation.created_at}",
                f"MODEL: {conversation.model or 'Unknown'}",
                "=" * 50,
                ""
            ]

            for msg in conversation.messages:
                role_name = "User" if msg.role == "user" else "Assistant" if msg.role == "assistant" else "System"
                lines.append(f"[{role_name} - {msg.timestamp}]")
                lines.append(msg.content)
                lines.append("-" * 30)
                lines.append("")

            content = "\n".join(lines)
            path.write_text(content, encoding="utf-8")
            logger.info(f"Exported conversation {conversation.id} to Text: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Failed to export conversation to Text: {e}")
            raise ExportError(f"Export to Text failed: {e}")

    @staticmethod
    def export_to_json(conversation: Conversation, file_path: Union[str, Path]) -> str:
        """Export conversation as JSON file."""
        try:
            path = Path(file_path)
            data = conversation.to_dict()
            content = json.dumps(data, indent=2, ensure_ascii=False)
            path.write_text(content, encoding="utf-8")
            logger.info(f"Exported conversation {conversation.id} to JSON: {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Failed to export conversation to JSON: {e}")
            raise ExportError(f"Export to JSON failed: {e}")
