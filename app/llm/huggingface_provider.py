import json
import requests
from typing import List, Dict, Generator, Optional
from app.llm.base import LLMProvider
from app.core.logger import logger
from app.core.exceptions import LocalAIException

DEFAULT_HF_MODELS = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-2-9b-it",
    "HuggingFaceH4/zephyr-7b-beta"
]

class HuggingFaceProvider(LLMProvider):
    """Hugging Face Serverless Inference API provider."""

    def __init__(self, api_key: str = "", default_models: Optional[List[str]] = None):
        self.api_key = api_key.strip()
        self.models = default_models or DEFAULT_HF_MODELS
        self.base_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

    def is_available(self) -> bool:
        """Check if API key is provided."""
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        """Return curated list of supported Hugging Face open-source models."""
        return self.models

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate response via Hugging Face chat completion API."""
        if not self.api_key:
            raise LocalAIException("Hugging Face API Key is missing. Please set your API key in Settings.")

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": model or self.models[0],
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API request failed: {e}")
            raise LocalAIException(f"Hugging Face API error: {e}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Generator[str, None, None]:
        """Stream response tokens via Hugging Face Serverless SSE API."""
        if not self.api_key:
            raise LocalAIException("Hugging Face API Key is missing. Please set your API key in Settings.")

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": model or self.models[0],
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        try:
            with requests.post(
                self.base_url,
                headers=self._headers(),
                json=payload,
                stream=True,
                timeout=60
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        line = line.strip()
                        if line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {}).get("content", "")
                                    if delta:
                                        yield delta
                            except json.JSONDecodeError:
                                continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face streaming failed: {e}")
            raise LocalAIException(f"Hugging Face streaming error: {e}")
