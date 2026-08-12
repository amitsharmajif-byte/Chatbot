"""
LocalAI Chat — Futuristic UI Theme Engine
==========================================
Premium dark theme with electric violet accents, glassmorphism effects,
and refined typography. Designed for a next-generation AI workspace.

Color System:
  Background:  #080A12 → #0F111C → #12141F → #181A28
  Accent:      #7C3AED (violet) / #6366F1 (indigo) / #22D3EE (cyan)
  Text:        #E2E8F0 (primary) / #94A3B8 (secondary) / #64748B (muted)

Spacing Scale: 4 / 8 / 12 / 16 / 24 / 32 / 48
"""


class StyleManager:
    """Centralized QSS theme manager for LocalAI Chat."""

    @staticmethod
    def get_style(theme: str = "dark") -> str:
        if theme == "light":
            return StyleManager.LIGHT_THEME
        return StyleManager.DARK_THEME

    # ─── FUTURISTIC DARK THEME ───────────────────────────────────────────

    DARK_THEME = """

    /* ══════════════════════════════════════════════════════════════════
       BASE WINDOW & GLOBAL DEFAULTS
       ══════════════════════════════════════════════════════════════════ */

    QMainWindow, QDialog {
        background-color: #080A12;
        color: #E2E8F0;
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif;
        font-size: 14px;
    }

    QWidget {
        color: #E2E8F0;
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif;
    }

    QToolTip {
        background-color: #181A28;
        color: #E2E8F0;
        border: 1px solid #2A2D45;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }

    /* ══════════════════════════════════════════════════════════════════
       HEADER BAR
       ══════════════════════════════════════════════════════════════════ */

    #HeaderBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0D0F1A, stop:1 #0A0C15);
        border-bottom: 1px solid #1A1D2E;
        min-height: 52px;
        max-height: 52px;
    }

    #AppTitleLabel {
        color: #E2E8F0;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    #AppTitleAccent {
        color: #A78BFA;
        font-size: 16px;
        font-weight: 700;
    }

    #StatusDot {
        min-width: 8px;
        max-width: 8px;
        min-height: 8px;
        max-height: 8px;
        border-radius: 4px;
        background-color: #10B981;
    }

    #StatusDotOffline {
        min-width: 8px;
        max-width: 8px;
        min-height: 8px;
        max-height: 8px;
        border-radius: 4px;
        background-color: #64748B;
    }

    #ModelLabel {
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
        padding-right: 4px;
    }

    /* ══════════════════════════════════════════════════════════════════
       SIDEBAR
       ══════════════════════════════════════════════════════════════════ */

    #Sidebar {
        background-color: #0B0D16;
        border-right: 1px solid #151828;
    }

    #NewChatButton {
        background-color: transparent;
        border: 1px solid #7C3AED;
        color: #C4B5FD;
        font-size: 13px;
        font-weight: 600;
        padding: 10px 16px;
        border-radius: 10px;
        text-align: center;
    }

    #NewChatButton:hover {
        background-color: rgba(124, 58, 237, 0.15);
        border-color: #8B5CF6;
        color: #DDD6FE;
    }

    #NewChatButton:pressed {
        background-color: rgba(124, 58, 237, 0.25);
        border-color: #A78BFA;
    }

    #SearchInput {
        background-color: #10121D;
        border: 1px solid #1A1D2E;
        border-radius: 8px;
        padding: 8px 12px;
        color: #E2E8F0;
        font-size: 13px;
        selection-background-color: rgba(124, 58, 237, 0.3);
    }

    #SearchInput:focus {
        border-color: rgba(124, 58, 237, 0.5);
        background-color: #12141F;
    }

    #SearchInput::placeholder {
        color: #475569;
    }

    #SidebarSectionLabel {
        color: #475569;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        padding: 8px 4px 4px 4px;
    }

    QListWidget#ChatHistoryList {
        background-color: transparent;
        border: none;
        outline: 0;
        padding: 0px;
    }

    QListWidget#ChatHistoryList::item {
        background-color: transparent;
        color: #94A3B8;
        border: none;
        border-radius: 8px;
        padding: 10px 12px;
        margin: 1px 0px;
        font-size: 13px;
    }

    QListWidget#ChatHistoryList::item:hover {
        background-color: rgba(124, 58, 237, 0.08);
        color: #C4B5FD;
    }

    QListWidget#ChatHistoryList::item:selected {
        background-color: rgba(124, 58, 237, 0.15);
        color: #E2E8F0;
        border-left: 3px solid #7C3AED;
        padding-left: 9px;
    }

    #SidebarSettingsButton {
        background-color: transparent;
        border: 1px solid #1A1D2E;
        border-radius: 8px;
        color: #64748B;
        font-size: 13px;
        padding: 8px 12px;
        text-align: left;
    }

    #SidebarSettingsButton:hover {
        background-color: rgba(100, 116, 139, 0.1);
        color: #94A3B8;
        border-color: #2A2D45;
    }

    /* ══════════════════════════════════════════════════════════════════
       COMBOBOX (Model Selector & Settings Dropdowns)
       ══════════════════════════════════════════════════════════════════ */

    QComboBox {
        background-color: #12141F;
        border: 1px solid #1E2035;
        border-radius: 8px;
        padding: 6px 12px;
        color: #E2E8F0;
        font-size: 13px;
        min-height: 28px;
        selection-background-color: rgba(124, 58, 237, 0.3);
    }

    QComboBox:hover {
        border-color: #2A2D45;
        background-color: #151828;
    }

    QComboBox:focus {
        border-color: rgba(124, 58, 237, 0.5);
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        border-left: 1px solid #1E2035;
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
    }

    QComboBox::down-arrow {
        image: none;
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #64748B;
    }

    QComboBox QAbstractItemView {
        background-color: #12141F;
        border: 1px solid #1E2035;
        border-radius: 8px;
        selection-background-color: rgba(124, 58, 237, 0.2);
        selection-color: #E2E8F0;
        color: #C4B5FD;
        padding: 4px;
        outline: 0;
    }

    QComboBox QAbstractItemView::item {
        padding: 6px 12px;
        min-height: 28px;
        border-radius: 6px;
    }

    QComboBox QAbstractItemView::item:hover {
        background-color: rgba(124, 58, 237, 0.12);
    }

    /* ══════════════════════════════════════════════════════════════════
       ICON BUTTONS (Header, Sidebar)
       ══════════════════════════════════════════════════════════════════ */

    QPushButton#IconButton {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 15px;
        padding: 4px;
        min-width: 34px;
        min-height: 34px;
        max-width: 34px;
        max-height: 34px;
    }

    QPushButton#IconButton:hover {
        background-color: rgba(124, 58, 237, 0.12);
        border-color: rgba(124, 58, 237, 0.3);
        color: #C4B5FD;
    }

    QPushButton#IconButton:pressed {
        background-color: rgba(124, 58, 237, 0.2);
    }

    /* ══════════════════════════════════════════════════════════════════
       CHAT AREA
       ══════════════════════════════════════════════════════════════════ */

    #ChatArea {
        background-color: #080A12;
        border: none;
    }

    /* ══════════════════════════════════════════════════════════════════
       SCROLLBARS
       ══════════════════════════════════════════════════════════════════ */

    QScrollBar:vertical {
        background: transparent;
        width: 6px;
        margin: 0;
        border: none;
    }

    QScrollBar::handle:vertical {
        background: rgba(100, 116, 139, 0.25);
        border-radius: 3px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: rgba(100, 116, 139, 0.45);
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
        background: none;
        border: none;
    }

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }

    QScrollBar:horizontal {
        background: transparent;
        height: 6px;
        margin: 0;
        border: none;
    }

    QScrollBar::handle:horizontal {
        background: rgba(100, 116, 139, 0.25);
        border-radius: 3px;
        min-width: 30px;
    }

    QScrollBar::handle:horizontal:hover {
        background: rgba(100, 116, 139, 0.45);
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
        background: none;
        border: none;
    }

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }

    /* ══════════════════════════════════════════════════════════════════
       INPUT CONTAINER & TEXT EDIT
       ══════════════════════════════════════════════════════════════════ */

    #InputContainer {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0E1019, stop:1 #0A0C15);
        border-top: 1px solid #151828;
        padding: 12px 24px 16px 24px;
    }

    #InputInnerFrame {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 12px;
        padding: 0px;
    }

    #InputInnerFrame:focus-within {
        border-color: rgba(124, 58, 237, 0.5);
    }

    #ChatInputEdit {
        background-color: transparent;
        border: none;
        color: #E2E8F0;
        font-size: 14px;
        padding: 12px 14px;
        selection-background-color: rgba(124, 58, 237, 0.3);
    }

    #SendButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C3AED, stop:1 #6366F1);
        border: none;
        border-radius: 10px;
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        padding: 0px;
    }

    #SendButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #8B5CF6, stop:1 #7C3AED);
    }

    #SendButton:pressed {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6D28D9, stop:1 #5B21B6);
    }

    #SendButton:disabled {
        background-color: #1E2035;
        color: #475569;
    }

    #StopButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #EF4444, stop:1 #DC2626);
        border: none;
        border-radius: 10px;
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        min-width: 40px;
        max-width: 40px;
        min-height: 40px;
        max-height: 40px;
        padding: 0px;
    }

    #StopButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #F87171, stop:1 #EF4444);
    }

    #AttachButton {
        background-color: transparent;
        border: 1px solid #1E2035;
        border-radius: 8px;
        color: #64748B;
        font-size: 16px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        padding: 0px;
    }

    #AttachButton:hover {
        background-color: rgba(124, 58, 237, 0.1);
        border-color: rgba(124, 58, 237, 0.3);
        color: #A78BFA;
    }

    /* ══════════════════════════════════════════════════════════════════
       MESSAGE CARDS
       ══════════════════════════════════════════════════════════════════ */

    #UserMessageCard {
        background-color: rgba(124, 58, 237, 0.08);
        border: 1px solid rgba(124, 58, 237, 0.12);
        border-radius: 12px;
        padding: 0px;
    }

    #AssistantMessageCard {
        background-color: #0F111C;
        border: 1px solid #151828;
        border-radius: 12px;
        padding: 0px;
    }

    #MessageRoleLabel {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    #UserRoleLabel {
        color: #C4B5FD;
        font-size: 12px;
        font-weight: 700;
    }

    #AssistantRoleLabel {
        color: #A78BFA;
        font-size: 12px;
        font-weight: 700;
    }

    #MessageTimestampLabel {
        color: #475569;
        font-size: 11px;
        font-weight: 400;
    }

    QPushButton#ActionButton {
        background-color: transparent;
        border: 1px solid #1A1D2E;
        border-radius: 6px;
        color: #64748B;
        font-size: 12px;
        padding: 4px 10px;
        min-height: 26px;
    }

    QPushButton#ActionButton:hover {
        background-color: rgba(124, 58, 237, 0.1);
        border-color: rgba(124, 58, 237, 0.25);
        color: #A78BFA;
    }

    /* ══════════════════════════════════════════════════════════════════
       WELCOME SCREEN
       ══════════════════════════════════════════════════════════════════ */

    #WelcomeContainer {
        background-color: transparent;
    }

    #WelcomeIcon {
        color: #7C3AED;
        font-size: 36px;
    }

    #WelcomeTitle {
        color: #E2E8F0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    #WelcomeSubtitle {
        color: #64748B;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    QPushButton#ChipButton {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 10px;
        color: #94A3B8;
        font-size: 13px;
        padding: 10px 16px;
        text-align: left;
    }

    QPushButton#ChipButton:hover {
        background-color: rgba(124, 58, 237, 0.1);
        border-color: rgba(124, 58, 237, 0.25);
        color: #C4B5FD;
    }

    QPushButton#ChipButton:pressed {
        background-color: rgba(124, 58, 237, 0.18);
    }

    /* ══════════════════════════════════════════════════════════════════
       SETTINGS DIALOG
       ══════════════════════════════════════════════════════════════════ */

    QDialog {
        background-color: #0B0D16;
    }

    QTabWidget::pane {
        background-color: #0B0D16;
        border: 1px solid #151828;
        border-top: none;
        border-radius: 0px 0px 10px 10px;
    }

    QTabBar {
        background-color: transparent;
    }

    QTabBar::tab {
        background-color: transparent;
        color: #64748B;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 18px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 2px;
    }

    QTabBar::tab:hover {
        color: #94A3B8;
        border-bottom-color: #2A2D45;
    }

    QTabBar::tab:selected {
        color: #C4B5FD;
        border-bottom-color: #7C3AED;
        font-weight: 600;
    }

    QLabel {
        color: #E2E8F0;
        font-size: 13px;
    }

    QLineEdit {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 8px;
        padding: 8px 12px;
        color: #E2E8F0;
        font-size: 13px;
        selection-background-color: rgba(124, 58, 237, 0.3);
    }

    QLineEdit:focus {
        border-color: rgba(124, 58, 237, 0.5);
        background-color: #12141F;
    }

    QTextEdit {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 8px;
        padding: 8px 12px;
        color: #E2E8F0;
        font-size: 13px;
        selection-background-color: rgba(124, 58, 237, 0.3);
    }

    QTextEdit:focus {
        border-color: rgba(124, 58, 237, 0.5);
        background-color: #12141F;
    }

    QCheckBox {
        color: #C8D0DC;
        font-size: 13px;
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #2A2D45;
        border-radius: 4px;
        background-color: #10121D;
    }

    QCheckBox::indicator:checked {
        background-color: #7C3AED;
        border-color: #7C3AED;
    }

    QCheckBox::indicator:hover {
        border-color: #7C3AED;
    }

    QSpinBox, QDoubleSpinBox {
        background-color: #10121D;
        border: 1px solid #1E2035;
        border-radius: 8px;
        padding: 6px 10px;
        color: #E2E8F0;
        font-size: 13px;
    }

    QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: rgba(124, 58, 237, 0.5);
    }

    QSpinBox::up-button, QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border: none;
        border-left: 1px solid #1E2035;
        border-top-right-radius: 8px;
        background-color: transparent;
    }

    QSpinBox::down-button, QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border: none;
        border-left: 1px solid #1E2035;
        border-bottom-right-radius: 8px;
        background-color: transparent;
    }

    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
        width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid #64748B;
    }

    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
        width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #64748B;
    }

    QSlider::groove:horizontal {
        height: 4px;
        background-color: #1E2035;
        border-radius: 2px;
    }

    QSlider::handle:horizontal {
        background-color: #7C3AED;
        border: none;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }

    QSlider::handle:horizontal:hover {
        background-color: #8B5CF6;
    }

    QSlider::sub-page:horizontal {
        background-color: #7C3AED;
        border-radius: 2px;
    }

    QGroupBox {
        background-color: #10121D;
        border: 1px solid #1A1D2E;
        border-radius: 10px;
        padding: 20px 16px 16px 16px;
        margin-top: 10px;
        font-size: 13px;
        font-weight: 600;
        color: #C4B5FD;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        left: 12px;
        color: #C4B5FD;
    }

    QPushButton#SaveButton {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C3AED, stop:1 #6366F1);
        border: none;
        border-radius: 8px;
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 24px;
        min-height: 34px;
    }

    QPushButton#SaveButton:hover {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #8B5CF6, stop:1 #7C3AED);
    }

    QPushButton#CancelButton {
        background-color: transparent;
        border: 1px solid #1E2035;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 24px;
        min-height: 34px;
    }

    QPushButton#CancelButton:hover {
        background-color: rgba(100, 116, 139, 0.1);
        border-color: #2A2D45;
        color: #C8D0DC;
    }

    QPushButton#DangerButton {
        background-color: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 8px;
        color: #F87171;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 16px;
        min-height: 34px;
    }

    QPushButton#DangerButton:hover {
        background-color: rgba(239, 68, 68, 0.2);
        border-color: rgba(239, 68, 68, 0.4);
        color: #FCA5A5;
    }

    QPushButton#TestConnectionButton {
        background-color: rgba(124, 58, 237, 0.12);
        border: 1px solid rgba(124, 58, 237, 0.25);
        border-radius: 8px;
        color: #A78BFA;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 14px;
        min-height: 30px;
    }

    QPushButton#TestConnectionButton:hover {
        background-color: rgba(124, 58, 237, 0.2);
        border-color: rgba(124, 58, 237, 0.4);
        color: #C4B5FD;
    }

    /* ══════════════════════════════════════════════════════════════════
       SCROLL-TO-BOTTOM BUTTON
       ══════════════════════════════════════════════════════════════════ */

    #ScrollToBottomButton {
        background-color: rgba(124, 58, 237, 0.2);
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 16px;
        color: #C4B5FD;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 16px;
        min-height: 32px;
    }

    #ScrollToBottomButton:hover {
        background-color: rgba(124, 58, 237, 0.3);
        border-color: rgba(124, 58, 237, 0.5);
    }

    /* ══════════════════════════════════════════════════════════════════
       SPLITTER
       ══════════════════════════════════════════════════════════════════ */

    QSplitter::handle {
        background-color: #151828;
        width: 1px;
    }

    /* ══════════════════════════════════════════════════════════════════
       MENU (Context Menus)
       ══════════════════════════════════════════════════════════════════ */

    QMenu {
        background-color: #12141F;
        border: 1px solid #1E2035;
        border-radius: 8px;
        padding: 4px;
        color: #E2E8F0;
        font-size: 13px;
    }

    QMenu::item {
        padding: 6px 24px 6px 12px;
        border-radius: 6px;
    }

    QMenu::item:selected {
        background-color: rgba(124, 58, 237, 0.15);
        color: #C4B5FD;
    }

    QMenu::separator {
        height: 1px;
        background-color: #1E2035;
        margin: 4px 8px;
    }

    /* ══════════════════════════════════════════════════════════════════
       INPUT DIALOG
       ══════════════════════════════════════════════════════════════════ */

    QInputDialog {
        background-color: #0B0D16;
    }

    /* ══════════════════════════════════════════════════════════════════
       MESSAGE BOX
       ══════════════════════════════════════════════════════════════════ */

    QMessageBox {
        background-color: #0B0D16;
    }

    QMessageBox QPushButton {
        background-color: #12141F;
        border: 1px solid #1E2035;
        border-radius: 6px;
        color: #E2E8F0;
        font-size: 13px;
        padding: 6px 20px;
        min-width: 80px;
        min-height: 30px;
    }

    QMessageBox QPushButton:hover {
        background-color: rgba(124, 58, 237, 0.15);
        border-color: rgba(124, 58, 237, 0.3);
    }

    """

    # ─── LIGHT THEME (minimal update for compatibility) ──────────────

    LIGHT_THEME = """

    QMainWindow, QDialog {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif;
        font-size: 14px;
    }

    QWidget {
        color: #1E293B;
        font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif;
    }

    #HeaderBar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        min-height: 52px;
        max-height: 52px;
    }

    #AppTitleLabel {
        color: #1E293B;
        font-size: 16px;
        font-weight: 700;
    }

    #Sidebar {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }

    #NewChatButton {
        background-color: #7C3AED;
        border: none;
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 600;
        padding: 10px 16px;
        border-radius: 10px;
    }

    #NewChatButton:hover {
        background-color: #6D28D9;
    }

    #SearchInput {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 12px;
        color: #1E293B;
        font-size: 13px;
    }

    #SearchInput:focus {
        border-color: #7C3AED;
    }

    #SidebarSectionLabel {
        color: #94A3B8;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        padding: 8px 4px 4px 4px;
    }

    QListWidget#ChatHistoryList {
        background-color: transparent;
        border: none;
        outline: 0;
    }

    QListWidget#ChatHistoryList::item {
        background-color: transparent;
        color: #475569;
        border-radius: 8px;
        padding: 10px 12px;
        margin: 1px 0px;
        font-size: 13px;
    }

    QListWidget#ChatHistoryList::item:hover {
        background-color: rgba(124, 58, 237, 0.06);
        color: #6D28D9;
    }

    QListWidget#ChatHistoryList::item:selected {
        background-color: rgba(124, 58, 237, 0.1);
        color: #1E293B;
        border-left: 3px solid #7C3AED;
    }

    #ChatArea {
        background-color: #FFFFFF;
    }

    QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 6px 12px;
        color: #1E293B;
        font-size: 13px;
        min-height: 28px;
    }

    QComboBox:hover { border-color: #CBD5E1; }
    QComboBox:focus { border-color: #7C3AED; }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 28px;
        border: none;
        border-left: 1px solid #E2E8F0;
    }

    QComboBox::down-arrow {
        image: none;
        width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #94A3B8;
    }

    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        selection-background-color: rgba(124, 58, 237, 0.1);
        color: #1E293B;
        padding: 4px;
    }

    QPushButton#IconButton {
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        color: #64748B;
        font-size: 15px;
        min-width: 34px; min-height: 34px;
        max-width: 34px; max-height: 34px;
    }

    QPushButton#IconButton:hover {
        background-color: rgba(124, 58, 237, 0.08);
        color: #7C3AED;
    }

    #InputContainer {
        background-color: #FFFFFF;
        border-top: 1px solid #E2E8F0;
        padding: 12px 24px 16px 24px;
    }

    #InputInnerFrame {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
    }

    #ChatInputEdit {
        background-color: transparent;
        border: none;
        color: #1E293B;
        font-size: 14px;
        padding: 12px 14px;
    }

    #SendButton {
        background-color: #7C3AED;
        border: none;
        border-radius: 10px;
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 700;
        min-width: 40px; max-width: 40px;
        min-height: 40px; max-height: 40px;
    }

    #SendButton:hover { background-color: #6D28D9; }
    #SendButton:disabled { background-color: #E2E8F0; color: #94A3B8; }

    #StopButton {
        background-color: #EF4444;
        border: none;
        border-radius: 10px;
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        min-width: 40px; max-width: 40px;
        min-height: 40px; max-height: 40px;
    }

    #AttachButton {
        background-color: transparent;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 16px;
        min-width: 36px; max-width: 36px;
        min-height: 36px; max-height: 36px;
    }

    #AttachButton:hover { border-color: #7C3AED; color: #7C3AED; }

    #UserMessageCard {
        background-color: rgba(124, 58, 237, 0.06);
        border: 1px solid rgba(124, 58, 237, 0.1);
        border-radius: 12px;
    }

    #AssistantMessageCard {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
    }

    #MessageRoleLabel { font-size: 12px; font-weight: 700; }
    #UserRoleLabel { color: #7C3AED; }
    #AssistantRoleLabel { color: #6D28D9; }
    #MessageTimestampLabel { color: #94A3B8; font-size: 11px; }

    QPushButton#ActionButton {
        background-color: transparent;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: #64748B;
        font-size: 12px;
        padding: 4px 10px;
        min-height: 26px;
    }

    QPushButton#ActionButton:hover {
        background-color: rgba(124, 58, 237, 0.08);
        color: #7C3AED;
    }

    #WelcomeTitle { color: #1E293B; font-size: 26px; font-weight: 700; }
    #WelcomeSubtitle { color: #94A3B8; font-size: 14px; }
    #WelcomeIcon { color: #7C3AED; font-size: 36px; }

    QPushButton#ChipButton {
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        color: #475569;
        font-size: 13px;
        padding: 10px 16px;
        text-align: left;
    }

    QPushButton#ChipButton:hover {
        background-color: rgba(124, 58, 237, 0.08);
        border-color: rgba(124, 58, 237, 0.2);
        color: #7C3AED;
    }

    QTabWidget::pane { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-top: none; }
    QTabBar::tab { background: transparent; color: #64748B; border: none; border-bottom: 2px solid transparent; padding: 10px 18px; font-size: 13px; }
    QTabBar::tab:hover { color: #475569; border-bottom-color: #CBD5E1; }
    QTabBar::tab:selected { color: #7C3AED; border-bottom-color: #7C3AED; font-weight: 600; }

    QGroupBox { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px 16px 16px 16px; margin-top: 10px; color: #7C3AED; }
    QGroupBox::title { color: #7C3AED; padding: 2px 12px; left: 12px; }

    QCheckBox { color: #1E293B; font-size: 13px; }
    QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #CBD5E1; border-radius: 4px; background-color: #FFFFFF; }
    QCheckBox::indicator:checked { background-color: #7C3AED; border-color: #7C3AED; }

    QSlider::groove:horizontal { height: 4px; background-color: #E2E8F0; border-radius: 2px; }
    QSlider::handle:horizontal { background-color: #7C3AED; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }
    QSlider::sub-page:horizontal { background-color: #7C3AED; border-radius: 2px; }

    QPushButton#SaveButton { background-color: #7C3AED; border: none; border-radius: 8px; color: #FFFFFF; font-size: 13px; font-weight: 600; padding: 8px 24px; min-height: 34px; }
    QPushButton#SaveButton:hover { background-color: #6D28D9; }
    QPushButton#CancelButton { background-color: transparent; border: 1px solid #E2E8F0; border-radius: 8px; color: #64748B; font-size: 13px; padding: 8px 24px; min-height: 34px; }
    QPushButton#DangerButton { background-color: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; color: #EF4444; font-size: 13px; font-weight: 600; padding: 8px 16px; }

    #SidebarSettingsButton { background-color: transparent; border: 1px solid #E2E8F0; border-radius: 8px; color: #64748B; font-size: 13px; padding: 8px 12px; }
    #SidebarSettingsButton:hover { background-color: rgba(124, 58, 237, 0.06); color: #7C3AED; }

    QScrollBar:vertical { background: transparent; width: 6px; }
    QScrollBar::handle:vertical { background: rgba(148, 163, 184, 0.3); border-radius: 3px; min-height: 30px; }
    QScrollBar::handle:vertical:hover { background: rgba(148, 163, 184, 0.5); }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

    QMenu { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 4px; }
    QMenu::item { padding: 6px 24px 6px 12px; border-radius: 6px; }
    QMenu::item:selected { background-color: rgba(124, 58, 237, 0.08); color: #7C3AED; }

    QToolTip { background-color: #1E293B; color: #E2E8F0; border: 1px solid #334155; border-radius: 6px; padding: 6px 10px; font-size: 12px; }

    #ScrollToBottomButton { background-color: rgba(124, 58, 237, 0.1); border: 1px solid rgba(124, 58, 237, 0.2); border-radius: 16px; color: #7C3AED; font-size: 12px; font-weight: 600; padding: 6px 16px; }

    QSplitter::handle { background-color: #E2E8F0; width: 1px; }
    """
