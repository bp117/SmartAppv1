import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDateTime
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
import queue
import time
import os

class LoadingDots(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.dots = ""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)  # Update every 500ms
        self.setStyleSheet(
            "QLabel {"
            "color: #666666;"
            "font-size: 24px;"
            "font-weight: bold;"
            "padding: 5px;"
            "background-color: #e6e0f0;"  # Lighter purple shade
            "border-radius: 15px;"
            "margin: 5px;"
            "}"
        )

    def update_dots(self):
        self.dots = (self.dots + "." if len(self.dots) < 3 else "")
        self.setText(self.dots)

    def stop(self):
        self.timer.stop()
        self.deleteLater()

class MessageBubble(QTextEdit):
    def __init__(self, text, timestamp, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlainText(text)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setMinimumWidth(250)
        self.setMaximumHeight(200)
        
        self.timestamp_label = QLabel(timestamp)
        self.timestamp_label.setStyleSheet(
            "QLabel {"
            "color: #666666;"
            "font-size: 10px;"
            "margin-top: 2px;"
            "}"
        )
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        doc_height = self.document().size().height()
        if doc_height + 20 <= self.maximumHeight():
            self.setFixedHeight(doc_height + 20)

class MessageWidget(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)
        
        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(10, 5, 10, 0)
        
        icon_label = QLabel()
        icon_size = QSize(24, 24)
        
        if is_user:
            icon = QIcon('user_icon.png')
            icon_label.setPixmap(icon.pixmap(icon_size))
        else:
            icon = QIcon('bot_icon.png')
            icon_label.setPixmap(icon.pixmap(icon_size))
        
        icon_label.setFixedSize(icon_size)
        
        timestamp = QDateTime.currentDateTime().toString("hh:mm AP")
        
        bubble = MessageBubble(text, timestamp)
        
        # Updated color scheme with purple shades
        bubble.setStyleSheet(
            "QTextEdit {"
            "border-radius: 15px;"
            "padding: 12px;"
            f"background-color: {'#d9d2e9' if is_user else '#e6e0f0'};"  # User: darker, Bot: lighter
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
            "background: #b4a7d6;"  # Purple shade for scrollbar
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
        
        msg_layout.addWidget(icon_label)
        msg_layout.addSpacing(8)
        msg_layout.addWidget(bubble)
        msg_layout.addStretch()
        
        timestamp_layout = QHBoxLayout()
        timestamp_layout.setContentsMargins(42, 0, 10, 5)
        timestamp_label = QLabel(timestamp)
        timestamp_label.setStyleSheet(
            "QLabel {"
            "color: #666666;"
            "font-size: 10px;"
            "}"
        )
        timestamp_layout.addWidget(timestamp_label)
        timestamp_layout.addStretch()
        
        main_layout.addLayout(msg_layout)
        main_layout.addLayout(timestamp_layout)
        
        self.setLayout(main_layout)
        self.bubble = bubble

    def resizeEvent(self, event):
        super().resizeEvent(event)
        available_width = self.width() - 100
        self.bubble.setMaximumWidth(min(available_width, 800))

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
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            "QScrollArea {"
            "border: none;"
            "background-color: white;"
            "}"
        )
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.addStretch()
        self.messages_widget.setStyleSheet(
            "QWidget {"
            "background-color: white;"
            "}"
        )
        
        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area)
        
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet(
            "QTextEdit {"
            "border: 1px solid #b4a7d6;"  # Purple border
            "border-radius: 5px;"
            "padding: 5px;"
            "}"
        )
        
        send_button = QPushButton("Send")
        send_button.setStyleSheet(
            "QPushButton {"
            "background-color: #b4a7d6;"  # Purple background
            "color: white;"
            "border: none;"
            "border-radius: 5px;"
            "padding: 8px 16px;"
            "}"
            "QPushButton:hover {"
            "background-color: #9982c7;"  # Darker purple on hover
            "}"
        )
        send_button.clicked.connect(self.send_message)
        
        self.message_input.installEventFilter(self)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

    def show_loading_indicator(self):
        # Remove existing loading dots if any
        if self.loading_dots:
            self.loading_dots.stop()
        
        # Create new loading indicator
        loading_widget = QWidget()
        loading_layout = QHBoxLayout(loading_widget)
        loading_layout.setContentsMargins(50, 0, 10, 0)  # Align with messages
        
        self.loading_dots = LoadingDots()
        loading_layout.addWidget(self.loading_dots)
        loading_layout.addStretch()
        
        # Add to messages layout
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, loading_widget)
        self.scroll_to_bottom()

    def hide_loading_indicator(self):
        if self.loading_dots:
            self.loading_dots.stop()
            self.loading_dots = None
            
    def handle_bot_response(self, message):
        self.hide_loading_indicator()
        self.add_bot_message(message)

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            self.add_user_message(message)
            self.message_input.clear()
            self.input_queue.put(message)
            self.show_loading_indicator()

    # ... Rest of the ChatWindow methods remain the same ...

class ChatWorker(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, input_queue, output_queue):
        super().__init__()
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.running = True
        
    def run(self):
        while self.running:
            try:
                message = self.input_queue.get(timeout=0.1)
                # Simulate longer processing time to show loading animation
                time.sleep(2)
                
                responses = [
                    f"I understand you're saying: {message}",
                    f"That's interesting! Here's what I think about '{message}'...",
                    f"Let me respond to your message: '{message}' with some thoughts...",
                    f"Thanks for sharing! Regarding '{message}', I have a few points to discuss..."
                ]
                import random
                response = random.choice(responses)
                
                self.output_queue.put(response)
                self.response_ready.emit(response)
                
            except queue.Empty:
                continue
                
    def stop(self):
        self.running = False


def create_default_icons():
    """Create default SVG icons if icon files don't exist"""
    user_svg = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="35" r="25" fill="#4CAF50"/>
        <path d="M50 65 C20 65 10 85 10 95 L90 95 C90 85 80 65 50 65" fill="#4CAF50"/>
    </svg>'''
    
    bot_svg = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect x="20" y="20" width="60" height="60" rx="10" fill="#2196F3"/>
        <circle cx="35" cy="45" r="5" fill="white"/>
        <circle cx="65" cy="45" r="5" fill="white"/>
        <rect x="35" y="60" width="30" height="5" fill="white"/>
    </svg>'''
    
    if not os.path.exists('user_icon.png'):
        with open('user_icon.svg', 'w') as f:
            f.write(user_svg)
        app = QApplication.instance() or QApplication([])
        icon = QIcon('user_icon.svg')
        pixmap = icon.pixmap(QSize(32, 32))
        pixmap.save('user_icon.png')
        os.remove('user_icon.svg')
        
    if not os.path.exists('bot_icon.png'):
        with open('bot_icon.svg', 'w') as f:
            f.write(bot_svg)
        app = QApplication.instance() or QApplication([])
        icon = QIcon('bot_icon.svg')
        pixmap = icon.pixmap(QSize(32, 32))
        pixmap.save('bot_icon.png')
        os.remove('bot_icon.svg')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
