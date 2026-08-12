import re
import html
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton, QApplication
)
from PySide6.QtGui import QTextDocument

try:
    import pygments
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


def markdown_to_html(md_text: str) -> str:
    """Simple robust Markdown to HTML converter with code block syntax highlighting."""
    if not md_text:
        return ""

    escaped = html.escape(md_text)

    # Process Fenced Code Blocks ```lang ... ```
    def replace_code_block(match):
        lang = match.group(1).strip().lower()
        code_content = html.unescape(match.group(2))

        highlighted_code = ""
        if PYGMENTS_AVAILABLE and lang:
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
                formatter = HtmlFormatter(nowrap=True, style="monokai")
                highlighted_code = pygments.highlight(code_content, lexer, formatter)
            except Exception:
                highlighted_code = html.escape(code_content)
        else:
            highlighted_code = html.escape(code_content)

        return (
            f'<div style="background-color: #0D0F1A; border: 1px solid #1E1E2E; border-radius: 6px; padding: 10px; margin: 8px 0; font-family: Consolas, monospace;">'
            f'<div style="font-size: 11px; color: #A78BFA; background-color: rgba(124, 58, 237, 0.1); padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 6px; font-weight: bold; text-transform: uppercase;">{lang if lang else "CODE"}</div>'
            f'<pre style="margin:0; white-space: pre-wrap; font-family: Consolas, monospace; color: #f8f8f2;">{highlighted_code}</pre>'
            f'</div>'
        )

    text = re.sub(r'```(\w*)\n([\s\S]*?)```', replace_code_block, escaped)

    # Process Inline Code `code`
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="background-color: #1E1E2E; color: #A78BFA; padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace;">\1</code>',
        text
    )

    # Process Bold **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)

    # Process Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)

    # Process Headers # H1, ## H2, ### H3
    text = re.sub(r'^### (.*$)', r'<h3 style="margin: 6px 0; color: #A78BFA;">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*$)', r'<h2 style="margin: 8px 0; color: #A78BFA;">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*$)', r'<h1 style="margin: 10px 0; color: #A78BFA;">\1</h1>', text, flags=re.MULTILINE)

    # Replace newlines with <br> inside regular text paragraphs
    paragraphs = text.split("\n\n")
    html_paragraphs = []
    for p in paragraphs:
        if not p.startswith('<div') and not p.startswith('<h'):
            p = p.replace("\n", "<br>")
        html_paragraphs.append(p)

    return f'<div style="color: inherit; font-size: 14px; line-height: 1.5;">{"".join(html_paragraphs)}</div>'


class MessageWidget(QWidget):
    """Custom Widget representing a single chat message card."""
    regenerate_requested = Signal()

    def __init__(self, role: str, content: str, timestamp: str = "", show_timestamp: bool = True, parent=None):
        super().__init__(parent)
        self.role = role
        self.raw_content = content
        self.timestamp = timestamp
        self.show_timestamp = show_timestamp

        self.is_streaming = False
        self.cursor_visible = True
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self._toggle_cursor)
        self.cursor_timer.setInterval(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        # Card container widget
        self.card = QWidget()
        if role == "user":
            self.card.setObjectName("UserMessageCard")
        else:
            self.card.setObjectName("AssistantMessageCard")

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)

        # Header Row (Role + Timestamp)
        header_layout = QHBoxLayout()
        role_label = QLabel("You" if role == "user" else "✦ LocalAI")
        if role == "user":
            role_label.setObjectName("UserRoleLabel")
        else:
            role_label.setObjectName("AssistantRoleLabel")

        time_label = QLabel(timestamp or "")
        time_label.setObjectName("MessageTimestampLabel")
        time_label.setVisible(show_timestamp)

        header_layout.addWidget(role_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        card_layout.addLayout(header_layout)

        # Text Browser Content View
        self.text_view = QTextBrowser()
        self.text_view.setOpenExternalLinks(True)
        self.text_view.setStyleSheet("background: transparent; border: none; color: #E2E8F0; font-size: 14px;")
        self.text_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.update_content(content)

        card_layout.addWidget(self.text_view)

        # Action Buttons Row (for assistant messages)
        if role == "assistant":
            actions_layout = QHBoxLayout()
            actions_layout.setSpacing(8)

            copy_btn = QPushButton("📋 Copy")
            copy_btn.setObjectName("ActionButton")
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(self.copy_content)

            regen_btn = QPushButton("🔄 Regenerate")
            regen_btn.setObjectName("ActionButton")
            regen_btn.setCursor(Qt.PointingHandCursor)
            regen_btn.clicked.connect(lambda: self.regenerate_requested.emit())

            actions_layout.addWidget(copy_btn)
            actions_layout.addWidget(regen_btn)
            actions_layout.addStretch()

            card_layout.addLayout(actions_layout)

        layout.addWidget(self.card)

    def set_streaming(self, is_streaming: bool):
        self.is_streaming = is_streaming
        if is_streaming:
            self.cursor_timer.start()
        else:
            self.cursor_timer.stop()
            self.cursor_visible = False
            self.update_content(self.raw_content)

    def _toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        if self.is_streaming:
            self.update_content(self.raw_content)

    def update_content(self, new_content: str):
        """Update content dynamically for live streaming."""
        self.raw_content = new_content
        display_content = new_content
        if self.is_streaming and self.cursor_visible:
            display_content += " ▌"

        formatted_html = markdown_to_html(display_content)
        self.text_view.setHtml(formatted_html)

        # Adjust height based on document content size
        self.text_view.document().adjustSize()
        doc_height = int(self.text_view.document().size().height()) + 20
        self.text_view.setFixedHeight(max(40, doc_height))

    def copy_content(self):
        """Copy raw text content to system clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)
