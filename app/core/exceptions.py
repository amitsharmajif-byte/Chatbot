class LocalAIException(Exception):
    """Base exception for LocalAI Chat application."""
    def __init__(self, message: str = "An unexpected error occurred."):
        super().__init__(message)
        self.message = message

class OllamaConnectionError(LocalAIException):
    """Raised when application cannot connect to Ollama server."""
    def __init__(self, host: str = "http://localhost:11434", message: str = None):
        if not message:
            message = f"Unable to connect to Ollama server at {host}. Please make sure Ollama is installed and running."
        super().__init__(message)
        self.host = host

class ModelNotFoundError(LocalAIException):
    """Raised when selected model is not installed in Ollama."""
    def __init__(self, model_name: str):
        message = f"The selected model '{model_name}' is not installed in Ollama."
        super().__init__(message)
        self.model_name = model_name

class DatabaseError(LocalAIException):
    """Raised when SQLite database operations fail."""
    pass

class ExportError(LocalAIException):
    """Raised when exporting chat conversations fails."""
    pass
