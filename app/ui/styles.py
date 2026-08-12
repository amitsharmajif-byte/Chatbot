class StyleManager:
    """QSS Stylesheets for LocalAI Chat themes."""

    DARK_THEME = """
    /* Main Window & Base Widgets */
    QMainWindow, QDialog {
        background-color: #14141d;
        color: #f1f5f9;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 14px;
    }

    QWidget {
        color: #f1f5f9;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    /* Sidebar Styling */
    #Sidebar {
        background-color: #1b1b26;
        border-right: 1px solid #282838;
    }

    #NewChatButton {
        background-color: #6366f1;
        color: #ffffff;
        font-weight: 600;
        font-size: 14px;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        text-align: left;
    }
    #NewChatButton:hover {
        background-color: #4f46e5;
    }
    #NewChatButton:pressed {
        background-color: #4338ca;
    }

    #SearchInput {
        background-color: #242433;
        color: #f1f5f9;
        border: 1px solid #333347;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    #SearchInput:focus {
        border: 1px solid #6366f1;
    }

    /* Sidebar List Items */
    QListWidget#ChatHistoryList {
        background-color: transparent;
        border: none;
        outline: none;
    }
    QListWidget#ChatHistoryList::item {
        background-color: transparent;
        color: #94a3b8;
        border-radius: 6px;
        padding: 8px 10px;
        margin-bottom: 2px;
    }
    QListWidget#ChatHistoryList::item:hover {
        background-color: #262636;
        color: #f1f5f9;
    }
    QListWidget#ChatHistoryList::item:selected {
        background-color: #2e2e42;
        color: #ffffff;
        font-weight: 600;
    }

    /* Header Bar */
    #HeaderBar {
        background-color: #181824;
        border-bottom: 1px solid #282838;
        padding: 8px 16px;
    }

    #AppTitleLabel {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
    }

    /* QComboBox Styling */
    QComboBox {
        background-color: #242433;
        color: #f1f5f9;
        border: 1px solid #333347;
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 140px;
        font-weight: 500;
    }
    QComboBox:hover {
        border-color: #6366f1;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: none;
    }
    QComboBox QAbstractItemView {
        background-color: #1f1f2e;
        color: #f1f5f9;
        border: 1px solid #333347;
        selection-background-color: #6366f1;
        selection-color: #ffffff;
        padding: 4px;
        border-radius: 6px;
    }

    /* IconButton */
    QPushButton#IconButton {
        background-color: #242433;
        border: 1px solid #333347;
        border-radius: 6px;
        color: #cbd5e1;
        padding: 6px;
    }
    QPushButton#IconButton:hover {
        background-color: #2e2e42;
        color: #ffffff;
        border-color: #6366f1;
    }

    /* Chat Area */
    #ChatArea {
        background-color: #14141d;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #2e2e42;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #474766;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* Input Container & Box */
    #InputContainer {
        background-color: #1b1b26;
        border-top: 1px solid #282838;
        padding: 12px 16px;
    }

    #ChatInputEdit {
        background-color: #242433;
        color: #f1f5f9;
        border: 1px solid #333347;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        line-height: 1.4;
    }
    #ChatInputEdit:focus {
        border-color: #6366f1;
    }

    #SendButton {
        background-color: #6366f1;
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 36px;
    }
    #SendButton:hover {
        background-color: #4f46e5;
    }

    #StopButton {
        background-color: #ef4444;
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        min-height: 36px;
    }
    #StopButton:hover {
        background-color: #dc2626;
    }

    #AttachButton {
        background-color: #242433;
        border: 1px solid #333347;
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px;
    }
    #AttachButton:hover {
        background-color: #2e2e42;
        color: #ffffff;
    }

    /* Message Cards */
    QTextBrowser {
        background-color: transparent;
        border: none;
        color: #f1f5f9;
    }
    #UserMessageCard QTextBrowser {
        color: #ffffff;
    }
    #AssistantMessageCard QTextBrowser {
        color: #f1f5f9;
    }

    #UserMessageCard {
        background-color: #252538;
        border: 1px solid #33334a;
        border-radius: 12px;
        padding: 12px 16px;
        margin-left: 60px;
        margin-right: 12px;
    }

    #AssistantMessageCard {
        background-color: #1d1d29;
        border: 1px solid #282838;
        border-radius: 12px;
        padding: 12px 16px;
        margin-left: 12px;
        margin-right: 60px;
    }

    #MessageRoleLabel {
        font-weight: 700;
        font-size: 13px;
        color: #a5b4fc;
    }

    #MessageTimestampLabel {
        font-size: 11px;
        color: #64748b;
    }

    /* Action Buttons in Message Card */
    QPushButton#ActionButton {
        background-color: transparent;
        border: 1px solid #33334a;
        border-radius: 4px;
        color: #94a3b8;
        padding: 4px 8px;
        font-size: 11px;
    }
    QPushButton#ActionButton:hover {
        background-color: #2e2e42;
        color: #ffffff;
        border-color: #6366f1;
    }

    /* Welcome Container */
    #WelcomeTitle {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
    }
    #WelcomeSubtitle {
        font-size: 14px;
        color: #94a3b8;
    }

    QPushButton#ChipButton {
        background-color: #1e1e2c;
        border: 1px solid #2a2a3e;
        border-radius: 8px;
        padding: 10px 14px;
        color: #cbd5e1;
        text-align: left;
    }
    QPushButton#ChipButton:hover {
        background-color: #27273a;
        border-color: #6366f1;
        color: #ffffff;
    }

    /* TabWidget in Settings */
    QTabWidget::pane {
        border: 1px solid #282838;
        background-color: #1b1b26;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #14141d;
        color: #94a3b8;
        padding: 8px 16px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #1b1b26;
        color: #ffffff;
        font-weight: 600;
        border-bottom: 2px solid #6366f1;
    }
    """

    LIGHT_THEME = """
    /* Main Window & Base Widgets */
    QMainWindow, QDialog {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 14px;
    }

    QWidget {
        color: #0f172a;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    /* Sidebar Styling */
    #Sidebar {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }

    #NewChatButton {
        background-color: #4f46e5;
        color: #ffffff;
        font-weight: 600;
        font-size: 14px;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        text-align: left;
    }
    #NewChatButton:hover {
        background-color: #4338ca;
    }

    #SearchInput {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    #SearchInput:focus {
        border: 1px solid #4f46e5;
    }

    /* Sidebar List Items */
    QListWidget#ChatHistoryList {
        background-color: transparent;
        border: none;
        outline: none;
    }
    QListWidget#ChatHistoryList::item {
        background-color: transparent;
        color: #475569;
        border-radius: 6px;
        padding: 8px 10px;
        margin-bottom: 2px;
    }
    QListWidget#ChatHistoryList::item:hover {
        background-color: #e2e8f0;
        color: #0f172a;
    }
    QListWidget#ChatHistoryList::item:selected {
        background-color: #e0e7ff;
        color: #3730a3;
        font-weight: 600;
    }

    /* Header Bar */
    #HeaderBar {
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding: 8px 16px;
    }

    #AppTitleLabel {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
    }

    /* QComboBox Styling */
    QComboBox {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 140px;
        font-weight: 500;
    }
    QComboBox:hover {
        border-color: #4f46e5;
    }

    /* IconButton */
    QPushButton#IconButton {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        color: #475569;
        padding: 6px;
    }
    QPushButton#IconButton:hover {
        background-color: #f1f5f9;
        color: #0f172a;
        border-color: #4f46e5;
    }

    /* Chat Area */
    #ChatArea {
        background-color: #ffffff;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94a3b8;
    }

    /* Input Container & Box */
    #InputContainer {
        background-color: #f8fafc;
        border-top: 1px solid #e2e8f0;
        padding: 12px 16px;
    }

    #ChatInputEdit {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
    }
    #ChatInputEdit:focus {
        border-color: #4f46e5;
    }

    #SendButton {
        background-color: #4f46e5;
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }
    #SendButton:hover {
        background-color: #4338ca;
    }

    #StopButton {
        background-color: #ef4444;
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }
    #StopButton:hover {
        background-color: #dc2626;
    }

    #AttachButton {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        color: #64748b;
        padding: 8px;
    }
    #AttachButton:hover {
        background-color: #f1f5f9;
        color: #0f172a;
    }

    /* Message Cards */
    #UserMessageCard {
        background-color: #e0e7ff;
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        padding: 12px 16px;
        margin-left: 60px;
        margin-right: 12px;
    }

    #AssistantMessageCard {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 16px;
        margin-left: 12px;
        margin-right: 60px;
    }

    #MessageRoleLabel {
        font-weight: 700;
        font-size: 13px;
        color: #4338ca;
    }

    #MessageTimestampLabel {
        font-size: 11px;
        color: #64748b;
    }

    QPushButton#ActionButton {
        background-color: transparent;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        color: #64748b;
        padding: 4px 8px;
        font-size: 11px;
    }
    QPushButton#ActionButton:hover {
        background-color: #e2e8f0;
        color: #0f172a;
    }

    /* Welcome Container */
    #WelcomeTitle {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    #WelcomeSubtitle {
        font-size: 14px;
        color: #64748b;
    }

    QPushButton#ChipButton {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        color: #334155;
        text-align: left;
    }
    QPushButton#ChipButton:hover {
        background-color: #e2e8f0;
        border-color: #4f46e5;
        color: #0f172a;
    }

    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #f1f5f9;
        color: #64748b;
        padding: 8px 16px;
    }
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #0f172a;
        font-weight: 600;
        border-bottom: 2px solid #4f46e5;
    }
    """

    @classmethod
    def get_style(cls, theme: str = "dark") -> str:
        """Return QSS stylesheet string for theme name."""
        if theme.lower() == "light":
            return cls.LIGHT_THEME
        return cls.DARK_THEME
