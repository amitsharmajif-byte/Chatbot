from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog
)
from PySide6.QtGui import QKeyEvent, QIcon, QFont

class ChatTextEdit(QTextEdit):
    """Custom multiline text edit with Enter / Shift+Enter key handling."""
    send_requested = Signal()

    def __init__(self, parent=None, enter_to_send: bool = True):
        super().__init__(parent)
        self.setObjectName("ChatInputEdit")
        self.enter_to_send = enter_to_send
        self.setPlaceholderText("Type your message... (Shift+Enter for new line)")
        self.setAcceptRichText(False)
        self.setMaximumHeight(150)
        self.setMinimumHeight(44)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key_Return, Qt.Key_Enter):
            if modifiers & Qt.ShiftModifier:
                super().keyPressEvent(event)
            elif modifiers & Qt.ControlModifier:
                self.send_requested.emit()
            elif self.enter_to_send:
                self.send_requested.emit()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)


class ChatInputBox(QWidget):
    """Input Box container containing attachment button, auto-resizing text edit, and send/stop button."""
    send_triggered = Signal(str, str)  # (text, attachment_path)
    stop_triggered = Signal()
    attachment_changed = Signal(str)

    def __init__(self, parent=None, enter_to_send: bool = True):
        super().__init__(parent)
        self.setObjectName("InputContainer")
        self.attachment_path = ""
        self.is_generating = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Attachment status banner
        self.attachment_banner = QWidget()
        self.attachment_banner.setVisible(False)
        banner_layout = QHBoxLayout(self.attachment_banner)
        banner_layout.setContentsMargins(4, 2, 4, 2)
        
        self.attachment_label = QLabel("📎 File attached")
        self.attachment_label.setStyleSheet("color: #6366f1; font-weight: 500; font-size: 12px;")
        
        remove_attach_btn = QPushButton("✕")
        remove_attach_btn.setFixedSize(20, 20)
        remove_attach_btn.setStyleSheet("border: none; color: #94a3b8; font-weight: bold; background: transparent;")
        remove_attach_btn.setCursor(Qt.PointingHandCursor)
        remove_attach_btn.clicked.connect(self.clear_attachment)

        banner_layout.addWidget(self.attachment_label)
        banner_layout.addWidget(remove_attach_btn)
        banner_layout.addStretch()

        layout.addWidget(self.attachment_banner)

        # Input Row Layout
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        # Attach button
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("AttachButton")
        self.attach_btn.setFixedSize(38, 38)
        self.attach_btn.setToolTip("Attach text file (.txt, .md, .csv, .json)")
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.clicked.connect(self.select_attachment)

        # Text Edit
        self.text_edit = ChatTextEdit(enter_to_send=enter_to_send)
        self.text_edit.send_requested.connect(self.on_send_clicked)

        # Send / Stop Button
        self.action_btn = QPushButton("Send ▶")
        self.action_btn.setObjectName("SendButton")
        self.action_btn.setMinimumWidth(80)
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.on_action_clicked)

        input_row.addWidget(self.attach_btn, 0, Qt.AlignBottom)
        input_row.addWidget(self.text_edit, 1)
        input_row.addWidget(self.action_btn, 0, Qt.AlignBottom)

        layout.addLayout(input_row)

    def set_enter_to_send(self, enabled: bool):
        self.text_edit.enter_to_send = enabled

    def select_attachment(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Text File",
            "",
            "Text Files (*.txt *.md *.csv *.json *.py *.html *.css *.js);;All Files (*)"
        )
        if file_path:
            self.attachment_path = file_path
            path_name = file_path.split("/")[-1].split("\\")[-1]
            self.attachment_label.setText(f"📎 Attached: {path_name}")
            self.attachment_banner.setVisible(True)
            self.attachment_changed.emit(self.attachment_path)

    def clear_attachment(self):
        self.attachment_path = ""
        self.attachment_banner.setVisible(False)
        self.attachment_changed.emit("")

    def set_generating_state(self, generating: bool):
        self.is_generating = generating
        if generating:
            self.action_btn.setText("Stop ⏹")
            self.action_btn.setObjectName("StopButton")
            self.attach_btn.setEnabled(False)
        else:
            self.action_btn.setText("Send ▶")
            self.action_btn.setObjectName("SendButton")
            self.attach_btn.setEnabled(True)
        # Force stylesheet update
        self.action_btn.style().unpolish(self.action_btn)
        self.action_btn.style().polish(self.action_btn)

    def on_action_clicked(self):
        if self.is_generating:
            self.stop_triggered.emit()
        else:
            self.on_send_clicked()

    def on_send_clicked(self):
        text = self.text_edit.toPlainText().strip()
        if text or self.attachment_path:
            self.send_triggered.emit(text, self.attachment_path)
            self.text_edit.clear()
            self.clear_attachment()
