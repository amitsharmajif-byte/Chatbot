from PySide6.QtCore import Qt, Signal, QThread, QObject, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame
)
from app.services.chat_service import ChatService
from app.ui.message_widget import MessageWidget
from app.ui.input_box import ChatInputBox
from app.core.logger import logger
from app.core.exceptions import OllamaConnectionError, ModelNotFoundError, LocalAIException


class StreamWorker(QObject):
    """Worker object running LLM streaming in a separate QThread."""
    token_received = Signal(str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        chat_service: ChatService,
        conversation_id: str,
        user_prompt: str,
        model_name: str,
        attachment_path: str = ""
    ):
        super().__init__()
        self.chat_service = chat_service
        self.conversation_id = conversation_id
        self.user_prompt = user_prompt
        self.model_name = model_name
        self.attachment_path = attachment_path
        self._is_cancelled = False

    def stop(self):
        self._is_cancelled = True

    @Slot()
    def run(self):
        try:
            for token in self.chat_service.send_message_stream(
                conversation_id=self.conversation_id,
                user_content=self.user_prompt,
                model_name=self.model_name,
                attachment_path=self.attachment_path
            ):
                if self._is_cancelled:
                    break
                self.token_received.emit(token)

            self.finished.emit()

        except Exception as e:
            logger.error(f"StreamWorker error: {e}")
            self.error_occurred.emit(str(e))
            self.finished.emit()


class WelcomeWidget(QWidget):
    """Welcome view displayed when starting a new chat."""
    chip_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        title = QLabel("Welcome to LocalAI Chat")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("100% Free & Local Open-Source AI Chatbot running on your machine.")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Sample prompt chips
        chips = [
            "💡 Explain machine learning concepts in simple terms",
            "🐍 Write a Python script to parse CSV files and sort rows",
            "📝 Draft a polite email requesting project deadline extension",
            "⚡ What are best practices for database query performance?"
        ]

        for chip_text in chips:
            btn = QPushButton(chip_text)
            btn.setObjectName("ChipButton")
            btn.setMinimumWidth(400)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, t=chip_text: self.chip_clicked.emit(t[2:].strip()))
            layout.addWidget(btn, 0, Qt.AlignCenter)


class ChatWindow(QWidget):
    """Main Chat Interface containing message scroll area and input box."""
    conversation_updated = Signal(str)  # conversation_id

    def __init__(self, chat_service: ChatService, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatArea")
        self.chat_service = chat_service
        self.current_conversation_id = ""
        self.current_model = ""

        self.thread = None
        self.worker = None
        self.current_assistant_widget = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll Area for Messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_layout.setSpacing(14)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)

        # Welcome view
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.chip_clicked.connect(self.send_prompt)
        self.scroll_layout.insertWidget(0, self.welcome_widget)

        layout.addWidget(self.scroll_area, 1)

        # Input Box
        self.input_box = ChatInputBox(enter_to_send=self.chat_service.settings.enter_to_send)
        self.input_box.send_triggered.connect(self.send_prompt)
        self.input_box.stop_triggered.connect(self.stop_generation)

        layout.addWidget(self.input_box, 0)

    def load_conversation(self, conversation_id: str, model_name: str = ""):
        """Load conversation messages into scroll view."""
        self.current_conversation_id = conversation_id
        if model_name:
            self.current_model = model_name

        self.clear_messages_view()

        conv = self.chat_service.load_conversation(conversation_id)
        if not conv or not conv.messages:
            self.welcome_widget.setVisible(True)
            return

        self.welcome_widget.setVisible(False)
        for msg in conv.messages:
            widget = MessageWidget(role=msg.role, content=msg.content, timestamp=msg.timestamp)
            if msg.role == "assistant":
                widget.regenerate_requested.connect(self.regenerate_last_response)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, widget)

        self.scroll_to_bottom()

    def clear_messages_view(self):
        """Remove all message cards from layout except stretch and welcome widget."""
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            widget = item.widget()
            if widget and widget != self.welcome_widget:
                widget.setParent(None)
                widget.deleteLater()

    def send_prompt(self, user_text: str, attachment_path: str = ""):
        """Handle sending user message and starting streaming worker."""
        if not user_text.strip() and not attachment_path:
            return

        if not self.current_conversation_id:
            conv = self.chat_service.create_new_conversation(self.current_model)
            self.current_conversation_id = conv.id

        self.welcome_widget.setVisible(False)

        # Append User Message Card
        display_text = user_text
        if attachment_path:
            filename = attachment_path.split("/")[-1].split("\\")[-1]
            display_text += f"\n\n📎 *[Attached: {filename}]*"

        user_widget = MessageWidget(role="user", content=display_text)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, user_widget)

        # Append Assistant Empty Card for streaming
        self.current_assistant_widget = MessageWidget(role="assistant", content="...")
        self.current_assistant_widget.regenerate_requested.connect(self.regenerate_last_response)
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, self.current_assistant_widget)

        self.scroll_to_bottom()
        self.input_box.set_generating_state(True)

        # Start QThread for streaming
        self.thread = QThread()
        self.worker = StreamWorker(
            chat_service=self.chat_service,
            conversation_id=self.current_conversation_id,
            user_prompt=user_text,
            model_name=self.current_model,
            attachment_path=attachment_path
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.token_received.connect(self.on_token_received)
        self.worker.error_occurred.connect(self.on_stream_error)
        self.worker.finished.connect(self.on_stream_finished)

        self.thread.start()

    def on_token_received(self, token: str):
        """Append streamed token to current assistant message card."""
        if self.current_assistant_widget:
            if self.current_assistant_widget.raw_content == "...":
                content = token
            else:
                content = self.current_assistant_widget.raw_content + token
            self.current_assistant_widget.update_content(content)
            self.scroll_to_bottom()

    def on_stream_finished(self):
        """Clean up streaming thread and reset input state."""
        self.input_box.set_generating_state(False)
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.conversation_updated.emit(self.current_conversation_id)

    def on_stream_error(self, error_msg: str):
        """Display error banner inside assistant card if streaming failed."""
        if self.current_assistant_widget:
            err_html = f"⚠️ **Error generating response:**\n{error_msg}"
            self.current_assistant_widget.update_content(err_html)

    def stop_generation(self):
        """Stop background worker generation."""
        if self.worker:
            self.worker.stop()
        self.on_stream_finished()

    def regenerate_last_response(self):
        """Regenerate assistant response for current conversation."""
        conv = self.chat_service.load_conversation(self.current_conversation_id)
        if not conv or not conv.messages:
            return

        last_user_msg = None
        for m in reversed(conv.messages):
            if m.role == "user":
                last_user_msg = m
                break

        if last_user_msg:
            self.send_prompt(last_user_msg.content)

    def scroll_to_bottom(self):
        """Scroll vertical scrollbar to maximum position."""
        vbar = self.scroll_area.verticalScrollBar()
        vbar.setValue(vbar.maximum())
