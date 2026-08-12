from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QSplitter, QMessageBox, QFrame, QApplication
)
from PySide6.QtGui import QShortcut, QKeySequence
from app.services.chat_service import ChatService
from app.llm.model_manager import ModelManager
from app.ui.sidebar import Sidebar
from app.ui.chat_window import ChatWindow
from app.ui.settings_window import SettingsWindow
from app.ui.styles import StyleManager
from app.ui.effects import PulsingDot
from app.core.config import APP_NAME, APP_VERSION
from app.core.logger import logger


class MainWindow(QMainWindow):
    """Main Application Window for LocalAI Chat."""

    def __init__(self, chat_service: ChatService, model_manager: ModelManager):
        super().__init__()
        self.chat_service = chat_service
        self.model_manager = model_manager

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1100, 750)
        self.setMinimumSize(800, 550)

        # ── Central Widget & Main Layout ──
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header Bar ──
        self.header_bar = QWidget()
        self.header_bar.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(self.header_bar)
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(12)

        # Logo / Title with Pulsing Status Dot
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        app_icon = QLabel("✦")
        app_icon.setObjectName("AppTitleAccent")

        app_title = QLabel(APP_NAME)
        app_title.setObjectName("AppTitleLabel")

        self.status_dot = PulsingDot(color="#10B981", size=8)
        self.status_dot.setToolTip("AI Status: Ready")

        title_layout.addWidget(app_icon)
        title_layout.addWidget(app_title)
        title_layout.addWidget(self.status_dot)

        # Model Selector Dropdown
        model_label = QLabel("Model:")
        model_label.setObjectName("ModelLabel")

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select active AI model")
        self.model_combo.setMinimumWidth(220)
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # Refresh Models Button
        refresh_models_btn = QPushButton("🔄")
        refresh_models_btn.setObjectName("IconButton")
        refresh_models_btn.setToolTip("Refresh available models")
        refresh_models_btn.setFixedSize(34, 34)
        refresh_models_btn.clicked.connect(self.populate_models)

        # Settings Button
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("IconButton")
        settings_btn.setToolTip("Open Settings (Ctrl+,)")
        settings_btn.setFixedSize(34, 34)
        settings_btn.clicked.connect(self.open_settings)

        header_layout.addWidget(title_container)
        header_layout.addStretch()
        header_layout.addWidget(model_label)
        header_layout.addWidget(self.model_combo)
        header_layout.addWidget(refresh_models_btn)
        header_layout.addWidget(settings_btn)

        main_layout.addWidget(self.header_bar)

        # ── Splitter Layout (Sidebar + ChatWindow) ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        self.sidebar = Sidebar(chat_service=self.chat_service)
        self.sidebar.new_chat_requested.connect(self.on_new_chat)
        self.sidebar.conversation_selected.connect(self.on_conversation_selected)
        self.sidebar.settings_requested.connect(self.open_settings)
        self.sidebar.conversation_deleted.connect(self.on_conversation_deleted)

        self.chat_window = ChatWindow(chat_service=self.chat_service)
        self.chat_window.conversation_updated.connect(self.on_conversation_updated)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.chat_window)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, 1)

        # ── Setup Keyboard Shortcuts ──
        self.setup_shortcuts()

        # ── Apply Theme ──
        self.apply_theme()

        # ── Populate Models & Check Health ──
        self.populate_models()
        QTimer.singleShot(600, self.check_ollama_health_on_launch)

    def apply_theme(self):
        """Apply theme QSS based on settings."""
        theme_name = self.chat_service.settings.theme
        qss = StyleManager.get_style(theme_name)
        self.setStyleSheet(qss)
        self.chat_window.input_box.set_enter_to_send(self.chat_service.settings.enter_to_send)

    def populate_models(self):
        """Query active LLM provider and populate model selector dropdown."""
        self.model_combo.blockSignals(True)
        self.model_combo.clear()

        self.model_manager.update_provider_from_settings(self.chat_service.settings)
        is_hf = self.chat_service.settings.provider.lower() == "huggingface"
        self.model_combo.setEditable(is_hf)

        models = self.model_manager.get_installed_models()
        if models:
            self.model_combo.addItems(models)
            default_model = self.model_manager.get_default_model(self.chat_service.settings.default_model)
            if default_model in models:
                self.model_combo.setCurrentText(default_model)
            elif is_hf and self.chat_service.settings.default_model:
                self.model_combo.setCurrentText(self.chat_service.settings.default_model)
            self.chat_window.current_model = self.model_combo.currentText()
            self.status_dot.set_active(True)
            self.status_dot.setToolTip("AI Status: Ready")
        else:
            self.model_combo.addItem("No models found")
            self.status_dot.set_active(False)
            self.status_dot.setToolTip("AI Status: No models available")

        self.model_combo.blockSignals(False)

    def check_ollama_health_on_launch(self):
        """Check active provider status on startup."""
        provider_name = self.chat_service.settings.provider.lower()
        if provider_name == "huggingface":
            if not self.chat_service.settings.huggingface_api_key:
                self.status_dot.set_active(False)
                self.status_dot.setToolTip("AI Status: API Key Needed")
                QMessageBox.information(
                    self,
                    "Hugging Face API Key Needed",
                    "Welcome to LocalAI Chat!\n\n"
                    "You have selected Hugging Face as your provider.\n"
                    "Please open Settings (⚙ icon at top right) and enter your free Hugging Face API key."
                )
            else:
                self.status_dot.set_active(True)
                self.status_dot.setToolTip("AI Status: Hugging Face Connected")
        else:
            if not self.model_manager.check_health():
                self.status_dot.set_active(False)
                self.status_dot.setToolTip("AI Status: Ollama Offline")
                QMessageBox.warning(
                    self,
                    "Ollama Not Detected",
                    "Unable to connect to local Ollama server at http://localhost:11434.\n\n"
                    "Option A: Start Ollama on your computer and click 🔄 refresh.\n"
                    "Option B: Open Settings (⚙ icon) and switch provider to 'Hugging Face (Serverless API)' using a free Hugging Face token!"
                )
            elif not self.model_manager.get_installed_models():
                self.status_dot.set_active(False)
                self.status_dot.setToolTip("AI Status: No Local Models")
                QMessageBox.information(
                    self,
                    "No Local Models Found",
                    "Welcome to LocalAI Chat!\n\n"
                    "To start chatting with Ollama, run in terminal:\n  ollama run qwen2.5\n\n"
                    "Or open Settings (⚙ icon) to switch to Hugging Face free API."
                )
            else:
                self.status_dot.set_active(True)
                self.status_dot.setToolTip("AI Status: Ollama Connected")

    def setup_shortcuts(self):
        """Register application global shortcuts."""
        QShortcut(QKeySequence("Ctrl+N"), self, self.on_new_chat)
        QShortcut(QKeySequence("Ctrl+K"), self, self.sidebar.focus_search)
        QShortcut(QKeySequence("Ctrl+,"), self, self.open_settings)
        QShortcut(QKeySequence("Escape"), self, self.chat_window.stop_generation)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, self.copy_last_assistant_response)

    def on_model_changed(self, model_name: str):
        """Update active model in chat window."""
        if model_name and model_name != "No models found":
            self.chat_window.current_model = model_name

    def on_new_chat(self):
        """Create new conversation session."""
        model_name = self.model_combo.currentText()
        if model_name == "No models found":
            model_name = ""
        conv = self.chat_service.create_new_conversation(model_name=model_name)
        self.sidebar.refresh_history()
        self.sidebar.select_conversation(conv.id)
        self.chat_window.new_chat()

    def on_conversation_selected(self, conversation_id: str):
        """Load selected conversation into chat window."""
        self.chat_window.load_conversation(conversation_id)

    def on_conversation_updated(self, conversation_id: str):
        """Refresh sidebar list when conversation title/messages update."""
        self.sidebar.refresh_history()
        self.sidebar.select_conversation(conversation_id)

    def on_conversation_deleted(self, conversation_id: str):
        """Handle active conversation deletion."""
        if self.chat_window.current_conversation_id == conversation_id:
            self.on_new_chat()

    def open_settings(self):
        """Open settings modal dialog."""
        dialog = SettingsWindow(
            chat_service=self.chat_service,
            model_manager=self.model_manager,
            parent=self
        )
        dialog.settings_saved.connect(self.on_settings_saved)
        dialog.exec_()

    def on_settings_saved(self):
        """Handle settings saved event."""
        self.apply_theme()
        self.populate_models()

    def copy_last_assistant_response(self):
        """Copy text of the last assistant response to clipboard."""
        conv_id = self.chat_window.current_conversation_id
        if conv_id:
            conv = self.chat_service.load_conversation(conv_id)
            if conv and conv.messages:
                for msg in reversed(conv.messages):
                    if msg.role == "assistant":
                        QApplication.clipboard().setText(msg.content)
                        break
