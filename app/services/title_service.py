import re
from typing import Optional
from app.core.logger import logger

class TitleService:
    """Service to automatically generate clean titles for conversations."""

    @staticmethod
    def generate_title_from_text(prompt: str, max_words: int = 6) -> str:
        """Generate a short title from user prompt text."""
        if not prompt or not prompt.strip():
            return "New Chat"

        # Remove code blocks, markdown symbols, and leading/trailing whitespace
        clean_text = re.sub(r"```[\s\S]*?```", "", prompt)
        clean_text = re.sub(r"[#*_`~>+\-\\\/|]", " ", clean_text)
        clean_text = " ".join(clean_text.split())

        if not clean_text:
            return "New Chat"

        words = clean_text.split()
        if len(words) <= max_words:
            title = " ".join(words)
        else:
            title = " ".join(words[:max_words]) + "..."

        # Capitalize title words appropriately
        return title.strip().capitalize()
