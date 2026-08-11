from abc import ABC, abstractmethod
from typing import List, Dict, Generator, Optional

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers (Ollama, local transformers, etc.)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider service is available/running."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Return list of installed/available model names."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a complete text response synchronously."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Generator[str, None, None]:
        """Stream response tokens chunk by chunk."""
        pass
