# LocalAI Chat

**LocalAI Chat** is a 100% free, privacy-first, local desktop AI chatbot application built with **Python 3.11+**, **PySide6 (Qt)**, and **Ollama**.

It provides a modern, clean, ChatGPT-like desktop experience running entirely offline on your computer. User conversations are stored locally in an SQLite database without sending any data to external cloud services or third-party APIs.

---

## 🌟 Key Features

* **100% Free & Local**: No API costs, subscriptions, or API keys required.
* **Modern PySide6 Desktop GUI**: Native Windows interface with custom dark and light themes, smooth scrolling, and chat bubbles.
* **Open-Source LLM Integration**: Connects to [Ollama](https://ollama.com) to run models like Qwen, Llama 3, Mistral, and Gemma locally.
* **Live Token Streaming**: Non-blocking streaming response tokens in real-time.
* **Rich Text & Code Block Rendering**: Supports Markdown, list formatting, bold/italics, and syntax-highlighted code blocks with a one-click copy button.
* **Local SQLite Database**: Persistent conversation history stored safely in `data/chatbot.db`.
* **Instant History Search**: Search previous conversations by title or message content.
* **Automatic Chat Titles**: Generates concise titles based on your initial prompt.
* **File Attachments**: Attach `.txt`, `.md`, `.csv`, `.json`, `.py` files directly to prompts.
* **Export Chat**: Export conversations to Markdown (`.md`), Text (`.txt`), or JSON (`.json`).
* **Keyboard Shortcuts**:
  * `Ctrl + N`: New Chat
  * `Ctrl + K`: Focus Search
  * `Ctrl + ,`: Settings
  * `Esc`: Stop Generation
  * `Ctrl + Shift + C`: Copy Last Response
* **Standalone Windows Executable**: Package as `LocalAI-Chat.exe` using PyInstaller.

---

## 📋 Requirements

* **Operating System**: Windows 10 / 11
* **Python**: 3.11 or higher
* **Ollama**: Download and install from [https://ollama.com](https://ollama.com)
* **RAM**:
  * 8 GB minimum (for 3B–7B models like `qwen2.5:3b` or `llama3.2:3b`)
  * 16 GB+ recommended (for 7B–14B models)

---

## 🚀 Quick Start Guide

### Step 1: Install Ollama & Pull a Model

1. Download and run the Ollama installer from [https://ollama.com/download](https://ollama.com/download).
2. Open Windows Command Prompt or PowerShell and pull a recommended model:
   ```bash
   ollama pull qwen2.5
   ```
   *(Alternative recommended models: `ollama pull llama3.2`, `ollama pull mistral`, `ollama pull gemma2`)*

### Step 2: Clone & Set Up LocalAI Chat

```powershell
git clone https://github.com/your-username/localai-chat.git
cd localai-chat

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Launch Application

```powershell
python main.py
```

---

## 🛠 Project Architecture

The application follows a clean modular architecture separating UI, business logic, persistence, and LLM providers:

```text
localai-chat/
│
├── main.py                    # Application launcher & global exception handler
├── requirements.txt           # Python dependencies
├── LocalAI-Chat.spec          # PyInstaller configuration
├── build.py                   # Build script for Windows .exe
├── README.md                  # Project documentation
├── LICENSE                    # MIT License
│
├── app/
│   ├── core/                  # Path configs, logger, custom exceptions
│   ├── database/              # SQLite database manager, models, repository
│   ├── llm/                   # LLMProvider interface, OllamaProvider, ModelManager
│   ├── services/              # ChatService, TitleService, ExportService
│   └── ui/                    # PySide6 MainWindow, Sidebar, ChatWindow, InputBox, Styles
│
├── data/                      # Local SQLite database (chatbot.db)
├── logs/                      # Rotating log files (app.log)
└── tests/                     # Unit test suite
```

### Extensible LLM Provider

The application abstracts LLMs behind the `LLMProvider` base class:

```python
class LLMProvider(ABC):
    def is_available(self) -> bool: ...
    def list_models(self) -> List[str]: ...
    def generate(self, messages, model, ...) -> str: ...
    def stream(self, messages, model, ...) -> Generator[str, None, None]: ...
```

This allows adding other backends (such as llama.cpp, vLLM, or LM Studio) without modifying the GUI or database layers.

---

## 📦 Packaging as Windows Executable (.exe)

You can build a standalone `LocalAI-Chat.exe` that runs without requiring Python installed:

```powershell
python build.py
```

The compiled executable will be saved in `dist/LocalAI-Chat.exe`.

> **Note**: The `.exe` does not bundle large LLM model files; models remain managed locally via Ollama.

---

## 🧪 Running Unit Tests

Run the test suite to verify database operations, LLM provider handling, and services:

```powershell
pytest tests/
```

---

## ❓ Troubleshooting

### 1. "Ollama Not Detected" Warning
* **Cause**: The Ollama background service is not running or port 11434 is blocked.
* **Fix**: Ensure Ollama is installed and running in your taskbar, then click the **🔄 Refresh** button in the header bar.

### 2. "No Local Models Found"
* **Cause**: Ollama is running, but no models have been pulled yet.
* **Fix**: Run `ollama pull qwen2.5` in Command Prompt to download a model.

### 3. Generation is Slow
* **Fix**: Use a smaller quantized model suited to your hardware:
  * GPU available: Models render fast via VRAM.
  * CPU only: Use smaller 3B models like `qwen2.5:3b` or `llama3.2:1b`.

---

## 📄 License

Distributed under the [MIT License](LICENSE).
