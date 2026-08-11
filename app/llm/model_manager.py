from typing import List, Optional
from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.core.logger import logger

class ModelManager:
    """Manages LLM providers, model detection, and health checks."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or OllamaProvider()

    def check_health(self) -> bool:
        """Check if active LLM provider service is available."""
        return self.provider.is_available()

    def get_installed_models(self) -> List[str]:
        """Fetch list of available/installed models."""
        try:
            return self.provider.list_models()
        except Exception as e:
            logger.warning(f"Error fetching installed models: {e}")
            return []

    def get_default_model(self, preferred_model: str = "") -> str:
        """Return preferred model if installed, else first available model, or empty string."""
        models = self.get_installed_models()
        if not models:
            return preferred_model
        if preferred_model and preferred_model in models:
            return preferred_model
        # Return first model available
        return models[0]
