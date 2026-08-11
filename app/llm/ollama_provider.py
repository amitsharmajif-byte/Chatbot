import json
import requests
from typing import List, Dict, Generator, Optional
from app.llm.base import LLMProvider
from app.core.config import DEFAULT_OLLAMA_HOST
from app.core.logger import logger
from app.core.exceptions import OllamaConnectionError, ModelNotFoundError

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider communicating over local HTTP REST API."""

    def __init__(self, host: str = DEFAULT_OLLAMA_HOST, timeout: int = 10):
        self.host = host.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if Ollama server responds at host root or /api/tags."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        """Fetch list of installed models from Ollama."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                names = []
                for m in models:
                    # e.g. "qwen2.5:latest" or "llama3.2:latest" -> extract display name
                    name = m.get("name") or m.get("model")
                    if name:
                        names.append(name)
                return sorted(names)
            return []
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to Ollama to list models: {e}")
            return []

    def _prepare_payload(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = True
    ) -> Dict:
        """Format payload for Ollama /api/chat endpoint."""
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        return {
            "model": model,
            "messages": formatted_messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }

    def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate full response synchronously."""
        if not self.is_available():
            raise OllamaConnectionError(self.host)

        payload = self._prepare_payload(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=120
            )
            if response.status_code == 404:
                raise ModelNotFoundError(model)
            response.raise_for_status()
            
            data = response.json()
            message = data.get("message", {})
            return message.get("content", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation request failed: {e}")
            raise OllamaConnectionError(self.host, message=f"Ollama error: {e}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Generator[str, None, None]:
        """Stream response tokens chunk by chunk from Ollama /api/chat."""
        if not self.is_available():
            raise OllamaConnectionError(self.host)

        payload = self._prepare_payload(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        try:
            with requests.post(
                f"{self.host}/api/chat",
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                if response.status_code == 404:
                    raise ModelNotFoundError(model)
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            data = json.loads(line)
                            delta = data.get("message", {}).get("content", "")
                            if delta:
                                yield delta
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise OllamaConnectionError(self.host, message=f"Ollama streaming error: {e}")
