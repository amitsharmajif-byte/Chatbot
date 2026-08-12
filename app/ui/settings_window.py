from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QComboBox,
    QSlider, QDoubleSpinBox, QSpinBox, QTextEdit, QCheckBox, QPushButton, QMessageBox, QFileDialog, QFormLayout, QGroupBox, QLineEdit
)
from app.services.chat_service import ChatService
from app.database.models import AppSettings
from app.llm.model_manager import ModelManager
from app.core.config import DB_PATH
from app.core.logger import logger

class SettingsWindow(QDialog):
    """Settings dialog managing user configuration and preferences."""
    settings_saved = Signal()

    def __init__(self, chat_service: ChatService, model_manager: ModelManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - LocalAI Chat")
        self.setMinimumSize(540, 460)
        self.chat_service = chat_service
        self.model_manager = model_manager
        self.settings: AppSettings = chat_service.settings

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Tab Widget
        self.tabs = QTabWidget()
        
        # 1. Model Tab
        self.model_tab = QWidget()
        self.init_model_tab()
        self.tabs.addTab(self.model_tab, "🤖 Model")

        # 2. Appearance Tab
        self.appearance_tab = QWidget()
        self.init_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "🎨 Appearance")

        # 3. Chat Preferences Tab
        self.chat_tab = QWidget()
        self.init_chat_tab()
        self.tabs.addTab(self.chat_tab, "💬 Chat")

        # 4. Data & Privacy Tab
        self.data_tab = QWidget()
        self.init_data_tab()
        self.tabs.addTab(self.data_tab, "🔒 Data & Privacy")

        main_layout.addWidget(self.tabs, 1)

        # Dialog Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("IconButton")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("SendButton")
        save_btn.clicked.connect(self.save_settings)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)

        main_layout.addLayout(btn_box)

    def init_model_tab(self):
        layout = QFormLayout(self.model_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Provider Selector
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Ollama (Local)", "Hugging Face (Serverless API)"])
        if self.settings.provider == "huggingface":
            self.provider_combo.setCurrentIndex(1)
        else:
            self.provider_combo.setCurrentIndex(0)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        layout.addRow("LLM Provider:", self.provider_combo)

        # Hugging Face API Key
        self.hf_key_edit = QLineEdit()
        self.hf_key_edit.setEchoMode(QLineEdit.Password)
        self.hf_key_edit.setPlaceholderText("hf_... (Get free API key from huggingface.co/settings/tokens)")
        self.hf_key_edit.setText(self.settings.huggingface_api_key)
        layout.addRow("Hugging Face Token:", self.hf_key_edit)

        # Default Model Dropdown
        self.model_combo = QComboBox()
        self.refresh_model_combo()

        layout.addRow("Default Model:", self.model_combo)

        # Temperature
        temp_layout = QHBoxLayout()
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(self.settings.temperature)

        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(int(self.settings.temperature * 100))

        self.temp_slider.valueChanged.connect(lambda v: self.temp_spin.setValue(v / 100.0))
        self.temp_spin.valueChanged.connect(lambda v: self.temp_slider.setValue(int(v * 100)))

        temp_layout.addWidget(self.temp_spin)
        temp_layout.addWidget(self.temp_slider)
        layout.addRow("Temperature (Creativity):", temp_layout)

        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 8192)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setValue(self.settings.max_tokens)
        layout.addRow("Max Tokens:", self.max_tokens_spin)

        # System Prompt
        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlainText(self.settings.system_prompt)
        self.system_prompt_edit.setMaximumHeight(100)
        layout.addRow("System Prompt:", self.system_prompt_edit)

    def on_provider_changed(self, index: int):
        self.refresh_model_combo()

    def refresh_model_combo(self):
        self.model_combo.clear()
        selected_provider = "huggingface" if self.provider_combo.currentIndex() == 1 else "ollama"
        temp_settings = AppSettings(
            provider=selected_provider,
            huggingface_api_key=self.hf_key_edit.text().strip(),
            ollama_host=self.settings.ollama_host
        )
        self.model_manager.update_provider_from_settings(temp_settings)
        installed_models = self.model_manager.get_installed_models()
        if installed_models:
            self.model_combo.addItems(installed_models)
            if self.settings.default_model in installed_models:
                self.model_combo.setCurrentText(self.settings.default_model)
        else:
            self.model_combo.addItem("No models detected")

    def init_appearance_tab(self):
        layout = QFormLayout(self.appearance_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.theme)
        layout.addRow("Application Theme:", self.theme_combo)

    def init_chat_tab(self):
        layout = QVBoxLayout(self.chat_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.streaming_cb = QCheckBox("Enable Response Streaming")
        self.streaming_cb.setChecked(self.settings.streaming_enabled)

        self.enter_send_cb = QCheckBox("Press Enter to send message (Shift+Enter for new line)")
        self.enter_send_cb.setChecked(self.settings.enter_to_send)

        self.timestamps_cb = QCheckBox("Show message timestamps")
        self.timestamps_cb.setChecked(self.settings.show_timestamps)

        self.auto_save_cb = QCheckBox("Automatically save conversation history to local database")
        self.auto_save_cb.setChecked(self.settings.auto_save)

        layout.addWidget(self.streaming_cb)
        layout.addWidget(self.enter_send_cb)
        layout.addWidget(self.timestamps_cb)
        layout.addWidget(self.auto_save_cb)
        layout.addStretch()

    def init_data_tab(self):
        layout = QVBoxLayout(self.data_tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Database location
        db_label = QLabel(f"<b>Database Location:</b> {DB_PATH}")
        db_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        db_label.setWordWrap(True)
        layout.addWidget(db_label)

        # Action Buttons
        clear_db_btn = QPushButton("🗑 Clear All Conversations")
        clear_db_btn.setStyleSheet("background-color: #ef4444; color: #ffffff; border: none; padding: 8px 14px; border-radius: 6px; font-weight: bold;")
        clear_db_btn.setCursor(Qt.PointingHandCursor)
        clear_db_btn.clicked.connect(self.clear_all_data)
        layout.addWidget(clear_db_btn)

        layout.addSpacing(10)

        # Privacy Box
        privacy_box = QGroupBox("Privacy Notice")
        privacy_layout = QVBoxLayout(privacy_box)
        privacy_msg = QLabel(
            "<b>Local-First Privacy:</b><br>"
            "Your conversations are stored strictly locally on this computer in an SQLite database.<br>"
            "No conversation data, telemetry, or analytics are sent to remote cloud servers."
        )
        privacy_msg.setWordWrap(True)
        privacy_msg.setStyleSheet("color: #a5b4fc; font-size: 12px; line-height: 1.4;")
        privacy_layout.addWidget(privacy_msg)

        layout.addWidget(privacy_box)
        layout.addStretch()

    def clear_all_data(self):
        confirm = QMessageBox.warning(
            self,
            "Delete All Data",
            "WARNING: This will permanently delete ALL local conversations and messages.\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.chat_service.delete_all_conversations()
            QMessageBox.information(self, "Data Cleared", "All conversation history has been cleared.")

    def save_settings(self):
        self.settings.provider = "huggingface" if self.provider_combo.currentIndex() == 1 else "ollama"
        self.settings.huggingface_api_key = self.hf_key_edit.text().strip()
        self.settings.default_model = self.model_combo.currentText()
        self.settings.temperature = self.temp_spin.value()
        self.settings.max_tokens = self.max_tokens_spin.value()
        self.settings.system_prompt = self.system_prompt_edit.toPlainText().strip()
        self.settings.theme = self.theme_combo.currentText()
        self.settings.streaming_enabled = self.streaming_cb.isChecked()
        self.settings.enter_to_send = self.enter_send_cb.isChecked()
        self.settings.show_timestamps = self.timestamps_cb.isChecked()
        self.settings.auto_save = self.auto_save_cb.isChecked()

        try:
            self.chat_service.repo.save_app_settings(self.settings)
            self.chat_service.reload_settings()
            self.settings_saved.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save settings: {e}")
