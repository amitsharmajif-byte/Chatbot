import sys
import os
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from app.core.config import APP_NAME, ORGANIZATION_NAME, APP_VERSION
from app.core.logger import logger
from app.database.database import Database
from app.database.repository import ChatRepository
from app.llm.ollama_provider import OllamaProvider
from app.llm.model_manager import ModelManager
from app.services.chat_service import ChatService
from app.ui.main_window import MainWindow

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to catch unhandled exceptions and log them."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"Unhandled Exception: {err_msg}")

    # Show user-friendly error dialog
    if QApplication.instance():
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{exc_value}\n\nDetails have been logged to logs/app.log"
        )

def main():
    """Application entry point."""
    sys.excepthook = handle_exception

    logger.info(f"Starting {APP_NAME} v{APP_VERSION}...")

    # Enable High DPI scaling for Qt
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)

    # Initialize core layers
    db = Database()
    repo = ChatRepository(db=db)
    llm_provider = OllamaProvider()
    model_manager = ModelManager(provider=llm_provider)
    chat_service = ChatService(repository=repo, llm_provider=llm_provider)

    # Launch Main Window
    window = MainWindow(chat_service=chat_service, model_manager=model_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
