import os
import json
import requests
from typing import List, Dict, Generator, Optional, Union
from app.llm.base import LLMProvider
from app.core.logger import logger
from app.core.exceptions import LocalAIException

DEFAULT_HF_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-2-9b-it",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
]

class HuggingFaceProvider(LLMProvider):
    """Hugging Face Serverless Inference API provider."""

    def __init__(self, api_key: str = "", default_models: Optional[List[str]] = None):
        self.raw_api_key = api_key
        self.api_key = self._resolve_api_key(api_key)
        self.models = default_models or DEFAULT_HF_MODELS
        self.base_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"

    def _resolve_api_key(self, provided_key: str) -> str:
        """Resolve API key from explicit parameter or environment variables."""
        key = provided_key.strip() if provided_key else ""
        if not key:
            for env_var in ("HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HF_API_TOKEN"):
                env_val = os.environ.get(env_var, "").strip()
                if env_val:
                    key = env_val
                    break

        # Strip surrounding quotes, newlines, or spaces
        return key.strip("'\" \t\r\n")

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
        """Return list of supported Hugging Face open-source models with dynamic discovery fallback."""
        discovered = []
        try:
            url = "https://huggingface.co/api/models?pipeline_tag=text-generation&sort=downloads&direction=-1&limit=15"
            headers = self._headers() if self.api_key else {}
            response = requests.get(url, headers=headers, timeout=4)
            if response.status_code == 200:
                data = response.json()
                for m in data:
                    model_id = m.get("id")
                    if model_id and model_id not in discovered:
                        discovered.append(model_id)
        except Exception as e:
            logger.warning(f"Live HF model discovery failed, using curated default list: {e}")

        # Combine curated defaults and discovered models
        combined = list(self.models)
        for d in discovered:
            if d not in combined:
                combined.append(d)
        return combined

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _parse_error_response(self, response: requests.Response) -> str:
        if response.status_code == 401:
            return (
                "Authentication Failed (HTTP 401: Invalid Token).\n"
                "Please verify your Hugging Face API Token in Settings (⚙) or in your .env file (HF_TOKEN).\n"
                "Get a free token at https://huggingface.co/settings/tokens with 'Read' permission."
            )

        try:
            data = response.json()
            if isinstance(data, dict):
                error = data.get("error") or data.get("message")
                if error:
                    if isinstance(error, dict):
                        return error.get("message", str(error))
                    return str(error)
            return response.text
        except Exception:
            return response.text

    def test_authentication(self) -> Dict[str, Union[bool, str]]:
        """Test A: Verify token authentication independently of any model."""
        if not self.is_available():
            return {
                "success": False,
                "message": "✗ Token missing. Please enter your Hugging Face Token (hf_...) in Settings or set HF_TOKEN in .env file."
            }

        try:
            url = "https://huggingface.co/api/whoami-v2"
            response = requests.get(url, headers=self._headers(), timeout=10)
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
        """Test B: Test if a specific model is supported and reachable on Serverless Router."""
        clean_model = model.strip() if (model and model.strip() and "No models" not in model) else self.models[0]
        payload = {
            "model": clean_model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5,
            "stream": False
        }

        try:
            response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=12)
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": f"✓ Model '{clean_model}' is active and reachable."
                }
            else:
                err_msg = self._parse_error_response(response)
                return {
                    "success": False,
                    "message": f"⚠️ Model Reachability Notice ({response.status_code}):\n{err_msg}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"✗ Inference Request Network Error: {e}"
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
        """Generate response via Hugging Face chat completion API."""
        if not self.api_key:
            raise LocalAIException("Hugging Face Token missing. Set your token in Settings (⚙) or HF_TOKEN in .env.")

        clean_model = model.strip() if (model and model.strip() and "No models" not in model) else self.models[0]
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": clean_model,
            "messages": formatted_messages,
            "temperature": min(max(temperature, 0.01), 1.0),
            "max_tokens": min(max_tokens, 1024),
            "stream": False
        }

        try:
            response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
            if response.status_code != 200:
                err_msg = self._parse_error_response(response)
                raise LocalAIException(f"Hugging Face Error ({response.status_code}): {err_msg}")

            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API request failed: {e}")
            raise LocalAIException(f"Hugging Face Connection Error: {e}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """Stream response tokens via Hugging Face Serverless SSE API."""
        if not self.api_key:
            raise LocalAIException("Hugging Face Token missing. Set your token in Settings (⚙) or HF_TOKEN in .env.")

        clean_model = model.strip() if (model and model.strip() and "No models" not in model) else self.models[0]
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        payload = {
            "model": clean_model,
            "messages": formatted_messages,
            "temperature": min(max(temperature, 0.01), 1.0),
            "max_tokens": min(max_tokens, 1024),
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
                if response.status_code != 200:
                    err_msg = self._parse_error_response(response)
                    raise LocalAIException(f"Hugging Face Error ({response.status_code}): {err_msg}")

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
            raise LocalAIException(f"Hugging Face Connection Error: {e}")
