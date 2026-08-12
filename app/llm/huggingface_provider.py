import os
import requests
from typing import List, Dict, Generator, Optional, Union
from huggingface_hub import InferenceClient
from app.llm.base import LLMProvider
from app.core.logger import logger
from app.core.exceptions import LocalAIException

DEFAULT_HF_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-2-9b-it",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
    "HuggingFaceH4/zephyr-7b-beta",
    "microsoft/Phi-3-mini-4k-instruct",
]

class HuggingFaceProvider(LLMProvider):
    """Hugging Face Serverless Inference API provider using official InferenceClient."""

    def __init__(self, api_key: str = "", default_models: Optional[List[str]] = None):
        self.raw_api_key = api_key
        self.api_key = self._resolve_api_key(api_key)
        self.models = default_models or list(DEFAULT_HF_MODELS)
        self._client: Optional[InferenceClient] = None

    def _resolve_api_key(self, provided_key: str) -> str:
        """Resolve API key from explicit parameter or environment variables."""
        key = provided_key.strip() if provided_key else ""
        if not key:
            for env_var in ("HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HF_API_TOKEN"):
                env_val = os.environ.get(env_var, "").strip()
                if env_val:
                    key = env_val
                    break
        return key.strip("'\" \t\r\n")

    def _get_client(self) -> InferenceClient:
        """Get or create a cached InferenceClient instance."""
        if self._client is None:
            self._client = InferenceClient(token=self.api_key)
        return self._client

    def get_token_info(self) -> Dict[str, Union[bool, int, str]]:
        """Return safe, non-sensitive diagnostic info about the current token."""
        token = self.api_key
        if not token:
            return {"present": False, "length": 0, "masked": "Not Configured"}
        masked = f"{token[:3]}...{token[-4:]}" if len(token) > 7 else "***"
        return {"present": True, "length": len(token), "masked": masked}

    def is_available(self) -> bool:
        """Check if API key is present."""
        return bool(self.api_key)

    def list_models(self) -> List[str]:
        """Return list of supported Hugging Face models with dynamic discovery fallback."""
        discovered = []
        try:
            url = "https://huggingface.co/api/models?pipeline_tag=text-generation&sort=downloads&direction=-1&limit=15"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            response = requests.get(url, headers=headers, timeout=4)
            if response.status_code == 200:
                data = response.json()
                for m in data:
                    model_id = m.get("id")
                    if model_id and model_id not in discovered:
                        discovered.append(model_id)
        except Exception as e:
            logger.warning(f"Live HF model discovery failed, using curated default list: {e}")

        combined = list(self.models)
        for d in discovered:
            if d not in combined:
                combined.append(d)
        return combined

    def _clean_model(self, model: str) -> str:
        """Sanitize model name, falling back to default if invalid."""
        if model and model.strip() and "No models" not in model:
            return model.strip()
        return self.models[0]

    def test_authentication(self) -> Dict[str, Union[bool, str]]:
        """Test A: Verify token authentication independently of any model."""
        if not self.is_available():
            return {
                "success": False,
                "message": "✗ Token missing. Please enter your Hugging Face Token (hf_...) in Settings or set HF_TOKEN in .env file."
            }
        try:
            url = "https://huggingface.co/api/whoami-v2"
            response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                username = data.get("name") or "Authenticated User"
                info = self.get_token_info()
                return {
                    "success": True,
                    "message": (
                        f"✓ Hugging Face Authentication Successful!\n"
                        f"• Account: @{username}\n"
                        f"• Token Status: Active ({info['masked']}, len: {info['length']})"
                    )
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "✗ Authentication Failed (HTTP 401: Invalid or Expired Token).\nPlease check your token."
                }
            else:
                return {
                    "success": False,
                    "message": f"✗ Authentication Probe Returned Status {response.status_code}: {response.text[:200]}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"✗ Network Connection Error: {e}"
            }

    def test_model_compatibility(self, model: str = "") -> Dict[str, Union[bool, str]]:
        """Test B: Test if a specific model is reachable via InferenceClient."""
        clean_model = self._clean_model(model)
        try:
            client = self._get_client()
            output = client.chat_completion(
                messages=[{"role": "user", "content": "hi"}],
                model=clean_model,
                max_tokens=5,
            )
            return {
                "success": True,
                "message": f"✓ Model '{clean_model}' is active and reachable."
            }
        except Exception as e:
            err_str = str(e)
            return {
                "success": False,
                "message": f"⚠ Model '{clean_model}' reachability notice:\n{err_str[:300]}"
            }

    def test_connection(self, model: str = "") -> Dict[str, Union[bool, str]]:
        """Combined test: Test A (Authentication) first, then Test B (Model Reachability)."""
        auth_res = self.test_authentication()
        if not auth_res["success"]:
            return auth_res

        model_res = self.test_model_compatibility(model)
        combined_msg = f"{auth_res['message']}\n\n{model_res['message']}"
        return {
            "success": True,
            "auth_success": True,
            "model_success": model_res["success"],
            "message": combined_msg
        }

    def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Generate response via Hugging Face InferenceClient chat completion."""
        if not self.api_key:
            raise LocalAIException("Hugging Face Token missing. Set your token in Settings (⚙) or HF_TOKEN in .env.")

        clean_model = self._clean_model(model)
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        try:
            client = self._get_client()
            output = client.chat_completion(
                messages=formatted_messages,
                model=clean_model,
                temperature=min(max(temperature, 0.01), 1.0),
                max_tokens=min(max_tokens, 4096),
            )
            choices = output.choices
            if choices and len(choices) > 0:
                return choices[0].message.content or ""
            return ""
        except Exception as e:
            logger.error(f"Hugging Face API request failed: {e}")
            raise LocalAIException(f"Hugging Face Error: {e}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream response tokens via Hugging Face InferenceClient."""
        if not self.api_key:
            raise LocalAIException("Hugging Face Token missing. Set your token in Settings (⚙) or HF_TOKEN in .env.")

        clean_model = self._clean_model(model)
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        try:
            client = self._get_client()
            stream_output = client.chat_completion(
                messages=formatted_messages,
                model=clean_model,
                temperature=min(max(temperature, 0.01), 1.0),
                max_tokens=min(max_tokens, 4096),
                stream=True,
            )
            for chunk in stream_output:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error(f"Hugging Face streaming failed: {e}")
            raise LocalAIException(f"Hugging Face Error: {e}")
