import unittest
from unittest.mock import patch, MagicMock
from app.llm.base import LLMProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.model_manager import ModelManager
from app.core.exceptions import OllamaConnectionError, ModelNotFoundError

class DummyLLMProvider(LLMProvider):
    def is_available(self) -> bool:
        return True
    def list_models(self):
        return ["qwen2.5", "llama3.2"]
    def generate(self, messages, model, system_prompt=None, temperature=0.7, max_tokens=2048):
        return "Dummy response"
    def stream(self, messages, model, system_prompt=None, temperature=0.7, max_tokens=2048):
        yield "Dummy "
        yield "stream"

class TestLLMProvider(unittest.TestCase):

    def test_base_provider_subclassing(self):
        provider = DummyLLMProvider()
        self.assertTrue(provider.is_available())
        self.assertEqual(provider.list_models(), ["qwen2.5", "llama3.2"])
        self.assertEqual(provider.generate([], "qwen2.5"), "Dummy response")

    @patch("requests.get")
    def test_ollama_is_available_true(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        provider = OllamaProvider(host="http://localhost:11434")
        self.assertTrue(provider.is_available())

    @patch("requests.get")
    def test_ollama_list_models(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [
                {"name": "qwen2.5:latest"},
                {"name": "mistral:latest"}
            ]
        }
        mock_get.return_value = mock_resp

        provider = OllamaProvider()
        models = provider.list_models()
        self.assertEqual(models, ["mistral:latest", "qwen2.5:latest"])

    def test_model_manager(self):
        dummy_provider = DummyLLMProvider()
        manager = ModelManager(provider=dummy_provider)
        self.assertTrue(manager.check_health())
        self.assertEqual(manager.get_installed_models(), ["qwen2.5", "llama3.2"])
        self.assertEqual(manager.get_default_model("llama3.2"), "llama3.2")
        self.assertEqual(manager.get_default_model("unknown"), "qwen2.5")

if __name__ == "__main__":
    unittest.main()
