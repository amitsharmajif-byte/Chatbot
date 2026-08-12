from typing import List, Optional
from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.huggingface_provider import HuggingFaceProvider
from app.database.models import AppSettings
from app.core.logger import logger

class ModelManager:
    """Manages LLM providers, model detection, and health checks."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or OllamaProvider()

    def update_provider_from_settings(self, settings: AppSettings) -> LLMProvider:
        """Update active provider based on AppSettings."""
        if settings.provider.lower() == "huggingface":
            self.provider = HuggingFaceProvider(api_key=settings.huggingface_api_key)
        else:
            self.provider = OllamaProvider(host=settings.ollama_host)
        return self.provider

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
        return models[0] if models else preferred_model
