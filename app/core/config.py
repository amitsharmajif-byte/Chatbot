import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from BASE_DIR if present
load_dotenv(dotenv_path=BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "chatbot.db"
LOG_FILE_PATH = LOGS_DIR / "app.log"

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_SYSTEM_PROMPT = "You are a helpful, respectful, and honest AI assistant."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048
DEFAULT_THEME = "dark"  # dark, light, system

APP_NAME = "LocalAI Chat"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "LocalAI"
