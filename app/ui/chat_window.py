from PySide6.QtCore import Qt, Signal, QObject, QThread, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel,
    QSizePolicy, QApplication
)
from app.ui.message_widget import MessageWidget
from app.ui.input_box import ChatInputBox
from app.ui.effects import AnimatedOrb, ThinkingDots
from app.services.chat_service import ChatService
from app.core.logger import logger
from app.core.exceptions import LocalAIException


class StreamWorker(QObject):
    """Background worker for streaming LLM responses without blocking UI."""
    token_received = Signal(str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, chat_service: ChatService, conversation_id: str,
                 user_text: str, model_name: str, attachment_path: str = ""):
        super().__init__()
        self.chat_service = chat_service
        self.conversation_id = conversation_id
        self.user_text = user_text
        self.model_name = model_name
        self.attachment_path = attachment_path

    def run(self):
        try:
            for token in self.chat_service.send_message_stream(
                conversation_id=self.conversation_id,
                user_content=self.user_text,
                model_name=self.model_name,
                attachment_path=self.attachment_path if self.attachment_path else None
            ):
                self.token_received.emit(token)
        except LocalAIException as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.error(f"Stream worker unexpected error: {e}")
            self.error_occurred.emit(f"Unexpected error: {e}")
        finally:
            self.finished.emit()


class WelcomeWidget(QWidget):
    """Futuristic welcome hero with animated orb and quick-start chips."""
    chip_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WelcomeContainer")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 32)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # ── Animated orb background ──
        self.orb = AnimatedOrb(self)
        self.orb.setFixedSize(300, 300)

        # ── Content over orb ──
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)
        content_layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("✦")
        icon.setObjectName("WelcomeIcon")
        icon.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(icon)

        title = QLabel("LocalAI")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title)

        subtitle = QLabel("Your private AI workspace")
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(subtitle)

        content_layout.addSpacing(32)

        # ── Quick-start chips ──
        chips_data = [
            "💡 Explain machine learning in simple terms",
            "📝 Write a Python function to sort a list",
            "🔍 Summarize a complex topic for beginners",
            "🚀 Help me debug my code"
        ]

        chips_container = QWidget()
        chips_container.setStyleSheet("background: transparent;")
        chips_layout = QVBoxLayout(chips_container)
        chips_layout.setSpacing(8)
        chips_layout.setContentsMargins(0, 0, 0, 0)

        # 2 rows of 2 chips
        for row_start in range(0, len(chips_data), 2):
            row = QHBoxLayout()
            row.setSpacing(8)
            for i in range(row_start, min(row_start + 2, len(chips_data))):
                chip = QPushButton(chips_data[i])
                chip.setObjectName("ChipButton")
                chip.setCursor(Qt.PointingHandCursor)
                chip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                chip_text = chips_data[i]
                chip.clicked.connect(lambda checked, t=chip_text: self.chip_clicked.emit(t))
                row.addWidget(chip)
            chips_layout.addLayout(row)

        content_layout.addWidget(chips_container)

        layout.addStretch(1)
        layout.addWidget(content, 0, Qt.AlignCenter)
        layout.addStretch(1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center the orb behind the content
        if hasattr(self, 'orb'):
            ox = (self.width() - self.orb.width()) // 2
            oy = (self.height() - self.orb.height()) // 2 - 40
            self.orb.move(ox, oy)


class ChatWindow(QWidget):
    """Main chat container with message scroll area, welcome hero, and input box."""
    conversation_updated = Signal(str)

    def __init__(self, chat_service: ChatService, parent=None):
        super().__init__(parent)
        self.chat_service = chat_service
        self.setObjectName("ChatArea")

        self.current_conversation_id = None
        self.current_model = ""
        self.current_assistant_widget = None
        self._accumulated_tokens = []
        self._worker = None
        self._thread = None

        # ── Main layout ──
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Scroll area for messages ──
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)

        # ── Centered message column ──
        self.message_column = QWidget()
        self.message_column.setStyleSheet("background: transparent;")
        self.message_column.setMaximumWidth(820)
        self.message_layout = QVBoxLayout(self.message_column)
        self.message_layout.setContentsMargins(24, 20, 24, 20)
        self.message_layout.setSpacing(12)

        # ── Welcome widget ──
        self.welcome_widget = WelcomeWidget()
        self.message_layout.addWidget(self.welcome_widget)
        self.message_layout.addStretch()

        # Center the message column
        column_container = QHBoxLayout()
        column_container.setContentsMargins(0, 0, 0, 0)
        column_container.addStretch()
        column_container.addWidget(self.message_column, 1)
        column_container.addStretch()
        self.scroll_layout.addLayout(column_container)

        scroll_area.setWidget(self.scroll_content)
        self.scroll_area = scroll_area
        self.scrollbar = scroll_area.verticalScrollBar()

        main_layout.addWidget(scroll_area, 1)

        # ── Scroll-to-bottom button ──
        self.scroll_to_bottom_btn = QPushButton("↓  New response")
        self.scroll_to_bottom_btn.setObjectName("ScrollToBottomButton")
        self.scroll_to_bottom_btn.setCursor(Qt.PointingHandCursor)
        self.scroll_to_bottom_btn.setVisible(False)
        self.scroll_to_bottom_btn.clicked.connect(self.scroll_to_bottom)
        # Position dynamically in resizeEvent

        # ── Input box ──
        self.input_box = ChatInputBox()
        main_layout.addWidget(self.input_box, 0)

        # ── Signal connections ──
        self.welcome_widget.chip_clicked.connect(self.send_prompt)
        self.input_box.send_triggered.connect(self.send_prompt)
        self.input_box.stop_triggered.connect(self.stop_generation)
        self.scrollbar.valueChanged.connect(self._on_scroll)

        # Track if user scrolled up
        self._user_scrolled_up = False
        self._auto_scroll = True

    def _on_scroll(self, value):
        """Track if user has scrolled away from bottom."""
        max_val = self.scrollbar.maximum()
        at_bottom = value >= max_val - 30
        self._user_scrolled_up = not at_bottom

        # Show/hide scroll-to-bottom button
        if self._user_scrolled_up and self.current_assistant_widget:
            self.scroll_to_bottom_btn.setVisible(True)
        else:
            self.scroll_to_bottom_btn.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position scroll-to-bottom button
        btn = self.scroll_to_bottom_btn
        btn_w, btn_h = 140, 32
        x = (self.width() - btn_w) // 2
        y = self.height() - self.input_box.height() - btn_h - 12
        btn.setGeometry(x, y, btn_w, btn_h)
        btn.raise_()

    def load_conversation(self, conversation_id: str, model_name: str = ""):
        """Load and display an existing conversation."""
        if model_name:
            self.current_model = model_name
        conv = self.chat_service.load_conversation(conversation_id)
        if not conv:
            return

        self.current_conversation_id = conversation_id
        self.clear_messages()
        self.welcome_widget.setVisible(False)
        if hasattr(self.welcome_widget, 'orb'):
            self.welcome_widget.orb.stop()

        for msg in conv.messages:
            widget = MessageWidget(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                show_timestamp=self.chat_service.settings.show_timestamps
            )
            if msg.role == "assistant":
                widget.regenerate_requested.connect(self.regenerate_last_response)
            # Insert before the stretch
            self.message_layout.insertWidget(self.message_layout.count() - 1, widget)

        QTimer.singleShot(50, self.scroll_to_bottom)

    def clear_messages(self):
        """Remove all message widgets from the layout."""
        while self.message_layout.count() > 2:  # Keep welcome_widget and stretch
            item = self.message_layout.takeAt(1)  # Take item after welcome
            if item and item.widget():
                item.widget().deleteLater()

    def new_chat(self):
        """Reset to new chat state with welcome screen."""
        self.current_conversation_id = None
        self.current_assistant_widget = None
        self.clear_messages()
        self.welcome_widget.setVisible(True)
        if hasattr(self.welcome_widget, 'orb'):
            self.welcome_widget.orb.start()
        self.input_box.text_edit.clear()
        self.input_box.clear_attachment()
        self.scroll_to_bottom_btn.setVisible(False)

    def send_prompt(self, text: str, attachment_path: str = ""):
        """Send user message and start streaming assistant response."""
        text = text.strip()
        if not text:
            return

        # Create conversation if needed
        if not self.current_conversation_id:
            conv = self.chat_service.create_new_conversation(model_name=self.current_model)
            self.current_conversation_id = conv.id

        # Hide welcome
        self.welcome_widget.setVisible(False)
        if hasattr(self.welcome_widget, 'orb'):
            self.welcome_widget.orb.stop()

        # Add user message widget
        user_widget = MessageWidget(
            role="user",
            content=text,
            show_timestamp=self.chat_service.settings.show_timestamps
        )
        self.message_layout.insertWidget(self.message_layout.count() - 1, user_widget)

        # Add assistant placeholder with thinking animation
        assistant_widget = MessageWidget(
            role="assistant",
            content="",
            show_timestamp=self.chat_service.settings.show_timestamps
        )
        assistant_widget.set_streaming(True)
        assistant_widget.regenerate_requested.connect(self.regenerate_last_response)
        self.message_layout.insertWidget(self.message_layout.count() - 1, assistant_widget)
        self.current_assistant_widget = assistant_widget
        self._accumulated_tokens = []

        # Set UI to generating state
        self.input_box.set_generating_state(True)
        self.input_box.text_edit.clear()
        self._user_scrolled_up = False

        QTimer.singleShot(30, self.scroll_to_bottom)

        # Start streaming in background thread
        self._thread = QThread()
        self._worker = StreamWorker(
            chat_service=self.chat_service,
            conversation_id=self.current_conversation_id,
            user_text=text,
            model_name=self.current_model,
            attachment_path=attachment_path
        )
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.token_received.connect(self.on_token_received)
        self._worker.error_occurred.connect(self.on_stream_error)
        self._worker.finished.connect(self.on_stream_finished)

        self._thread.start()

    def on_token_received(self, token: str):
        """Append streamed token to assistant message."""
        self._accumulated_tokens.append(token)
        full_text = "".join(self._accumulated_tokens)

        if self.current_assistant_widget:
            self.current_assistant_widget.update_content(full_text)

        if not self._user_scrolled_up:
            self.scroll_to_bottom()

    def on_stream_error(self, error_msg: str):
        """Display error in assistant message card."""
        if self.current_assistant_widget:
            self.current_assistant_widget.set_streaming(False)
            self.current_assistant_widget.update_content(
                f"⚠️ **Error generating response:**\n{error_msg}"
            )

    def on_stream_finished(self):
        """Clean up after streaming completes."""
        if self.current_assistant_widget:
            self.current_assistant_widget.set_streaming(False)

        self.input_box.set_generating_state(False)
        self.current_assistant_widget = None

        # Clean up thread
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(3000)

        self._worker = None
        self._thread = None

        if self.current_conversation_id:
            self.conversation_updated.emit(self.current_conversation_id)

    def stop_generation(self):
        """Stop the active streaming generation."""
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(2000)

        if self.current_assistant_widget:
            self.current_assistant_widget.set_streaming(False)

        self.input_box.set_generating_state(False)
        self.current_assistant_widget = None
        self._worker = None
        self._thread = None

    def regenerate_last_response(self):
        """Regenerate the last assistant response."""
        if not self.current_conversation_id:
            return

        conv = self.chat_service.load_conversation(self.current_conversation_id)
        if not conv or not conv.messages:
            return

        # Find last user message
        last_user_msg = None
        for msg in reversed(conv.messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break

        if last_user_msg:
            # Remove last assistant widget
            count = self.message_layout.count()
            for i in range(count - 1, -1, -1):
                item = self.message_layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), MessageWidget):
                    w = item.widget()
                    if hasattr(w, 'role') and w.role == "assistant":
                        self.message_layout.removeWidget(w)
                        w.deleteLater()
                        break

            self.send_prompt(last_user_msg)

    def scroll_to_bottom(self):
        """Scroll chat to the bottom."""
        QApplication.processEvents()
        self.scrollbar.setValue(self.scrollbar.maximum())
        self.scroll_to_bottom_btn.setVisible(False)
