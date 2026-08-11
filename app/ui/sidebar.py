from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QMenu, QInputDialog, QMessageBox, QFileDialog, QLabel
)
from app.services.chat_service import ChatService
from app.services.export_service import ExportService
from app.database.models import Conversation
from app.core.logger import logger

class Sidebar(QWidget):
    """Sidebar navigation bar managing conversation history, search, and settings."""
    new_chat_requested = Signal()
    conversation_selected = Signal(str)  # conversation_id
    settings_requested = Signal()
    conversation_deleted = Signal(str)

    def __init__(self, chat_service: ChatService, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)
        self.chat_service = chat_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(12)

        # "+ New Chat" Button
        self.new_chat_btn = QPushButton("+ New Chat")
        self.new_chat_btn.setObjectName("NewChatButton")
        self.new_chat_btn.setCursor(Qt.PointingHandCursor)
        self.new_chat_btn.setToolTip("Start a new conversation (Ctrl+N)")
        self.new_chat_btn.clicked.connect(lambda: self.new_chat_requested.emit())
        layout.addWidget(self.new_chat_btn)

        # Search Input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("🔍 Search conversations... (Ctrl+K)")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)

        # Section Header
        history_header = QLabel("Chat History")
        history_header.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-top: 6px;")
        layout.addWidget(history_header)

        # History ListWidget
        self.history_list = QListWidget()
        self.history_list.setObjectName("ChatHistoryList")
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        self.history_list.itemClicked.connect(self.on_item_clicked)

        layout.addWidget(self.history_list, 1)

        # Settings Button at bottom
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setObjectName("IconButton")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(lambda: self.settings_requested.emit())
        layout.addWidget(self.settings_btn)

        self.refresh_history()

    def refresh_history(self, search_query: str = ""):
        """Reload and display conversations in history list."""
        self.history_list.clear()
        if search_query:
            conversations = self.chat_service.search_conversations(search_query)
        else:
            conversations = self.chat_service.list_conversations()

        for conv in conversations:
            item = QListWidgetItem(f"💬  {conv.title}")
            item.setData(Qt.UserRole, conv.id)
            item.setToolTip(f"Model: {conv.model or 'Default'}\nUpdated: {conv.updated_at[:16]}")
            self.history_list.addItem(item)

    def select_conversation(self, conversation_id: str):
        """Programmatically select item in history list."""
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            if item.data(Qt.UserRole) == conversation_id:
                self.history_list.setCurrentItem(item)
                break

    def on_item_clicked(self, item: QListWidgetItem):
        conv_id = item.data(Qt.UserRole)
        if conv_id:
            self.conversation_selected.emit(conv_id)

    def on_search_text_changed(self, text: str):
        self.refresh_history(search_query=text)

    def focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def show_context_menu(self, position):
        """Right-click context menu for selected conversation."""
        item = self.history_list.itemAt(position)
        if not item:
            return

        conv_id = item.data(Qt.UserRole)
        conv = self.chat_service.load_conversation(conv_id)
        if not conv:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("✏ Rename Chat")
        export_menu = menu.addMenu("📥 Export Chat")
        export_md = export_menu.addAction("Markdown (.md)")
        export_txt = export_menu.addAction("Text (.txt)")
        export_json = export_menu.addAction("JSON (.json)")
        menu.addSeparator()
        delete_action = menu.addAction("🗑 Delete Chat")

        action = menu.exec_(self.history_list.viewport().mapToGlobal(position))

        if action == rename_action:
            new_title, ok = QInputDialog.getText(self, "Rename Chat", "New title:", QLineEdit.Normal, conv.title)
            if ok and new_title.strip():
                self.chat_service.repo.update_conversation_title(conv_id, new_title.strip())
                self.refresh_history(self.search_input.text())

        elif action == export_md:
            self._export_dialog(conv, "Markdown Files (*.md)", ExportService.export_to_markdown)
        elif action == export_txt:
            self._export_dialog(conv, "Text Files (*.txt)", ExportService.export_to_txt)
        elif action == export_json:
            self._export_dialog(conv, "JSON Files (*.json)", ExportService.export_to_json)

        elif action == delete_action:
            confirm = QMessageBox.question(
                self,
                "Delete Chat",
                f"Are you sure you want to delete '{conv.title}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.chat_service.delete_conversation(conv_id)
                self.refresh_history(self.search_input.text())
                self.conversation_deleted.emit(conv_id)

    def _export_dialog(self, conv: Conversation, filter_str: str, export_func):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            f"{conv.title.replace(' ', '_')}",
            filter_str
        )
        if file_path:
            try:
                export_func(conv, file_path)
                QMessageBox.information(self, "Export Successful", f"Exported conversation to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))
