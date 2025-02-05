import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDateTime
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
import queue
import time
import os

# ... [LoadingDots class remains the same] ...

class MessageBubble(QTextEdit):
    def __init__(self, text, timestamp, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlainText(text)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumWidth(250)
        self.setMaximumHeight(200)
        
        # Calculate and set text margins for better text display
        document_margin = 12  # This matches the padding in the stylesheet
        self.document().setDocumentMargin(document_margin)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Adjust height based on content
        doc_height = self.document().size().height()
        if doc_height + 20 <= self.maximumHeight():
            self.setFixedHeight(doc_height + 20)

class MessageWidget(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(2)
        
        self.msg_layout = QHBoxLayout()
        self.msg_layout.setContentsMargins(10, 5, 10, 0)
        
        # Icon setup
        self.icon_label = QLabel()
        icon_size = QSize(24, 24)
        
        if is_user:
            icon = QIcon('user_icon.png')
            self.icon_label.setPixmap(icon.pixmap(icon_size))
        else:
            icon = QIcon('bot_icon.png')
            self.icon_label.setPixmap(icon.pixmap(icon_size))
        
        self.icon_label.setFixedSize(icon_size)
        
        timestamp = QDateTime.currentDateTime().toString("hh:mm AP")
        
        self.bubble = MessageBubble(text, timestamp)
        self.is_user = is_user  # Store is_user for styling purposes
        
        # Updated color scheme with purple shades
        self.bubble.setStyleSheet(
            "QTextEdit {"
            "border-radius: 15px;"
            "padding: 12px;"
            f"background-color: {'#d9d2e9' if is_user else '#e6e0f0'};"
            "color: #202124;"
            "font-size: 13px;"
            "line-height: 1.4;"
            "}"
            "QScrollBar:vertical {"
            "width: 8px;"
            "background: transparent;"
            "margin: 0px 0px 0px 0px;"
            "}"
            "QScrollBar::handle:vertical {"
            "background: #b4a7d6;"
            "border-radius: 4px;"
            "min-height: 20px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "background: none;"
            "}"
        )
        
        # Setup message layout
        self.msg_layout.addWidget(self.icon_label)
        self.msg_layout.addSpacing(8)
        self.msg_layout.addWidget(self.bubble)
        self.msg_layout.addStretch()
        
        # Setup timestamp layout
        self.timestamp_layout = QHBoxLayout()
        self.timestamp_layout.setContentsMargins(42, 0, 10, 5)
        self.timestamp_label = QLabel(timestamp)
        self.timestamp_label.setStyleSheet(
            "QLabel {"
            "color: #666666;"
            "font-size: 10px;"
            "}"
        )
        self.timestamp_layout.addWidget(self.timestamp_label)
        self.timestamp_layout.addStretch()
        
        # Add layouts to main layout
        self.main_layout.addLayout(self.msg_layout)
        self.main_layout.addLayout(self.timestamp_layout)
        
        self.setLayout(self.main_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Calculate 80% of the window width, minus margins and icon space
        window = self.window()
        if window:
            total_window_width = window.width()
            margin_space = 100  # Account for margins, icon, and spacing
            max_bubble_width = int(total_window_width * 0.8) - margin_space
            min_bubble_width = 250  # Minimum width for the bubble
            
            # Set bubble width between minimum and maximum bounds
            optimal_width = max(min_bubble_width, min(max_bubble_width, 800))
            self.bubble.setFixedWidth(optimal_width)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Application")
        self.setMinimumSize(600, 400)
        
        create_default_icons()
        
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        self.init_ui()
        
        self.worker = ChatWorker(self.input_queue, self.output_queue)
        self.worker.response_ready.connect(self.handle_bot_response)
        self.worker.start()
        
        self.loading_dots = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Force all message widgets to update their size
        for i in range(self.messages_layout.count()):
            widget = self.messages_layout.itemAt(i).widget()
            if isinstance(widget, MessageWidget):
                widget.resizeEvent(event)
    
    # ... [Rest of the ChatWindow implementation remains the same] ...