import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPalette, QColor, QIcon
import queue
import time
import os

class MessageWidget(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        
        # Create icon label
        icon_label = QLabel()
        icon_size = QSize(32, 32)
        
        # Set icons based on whether it's a user or bot message
        if is_user:
            icon = QIcon('user_icon.png')  # Replace with your user icon path
            icon_label.setPixmap(icon.pixmap(icon_size))
        else:
            icon = QIcon('bot_icon.png')  # Replace with your bot icon path
            icon_label.setPixmap(icon.pixmap(icon_size))
        
        icon_label.setFixedSize(icon_size)
        
        # Create message bubble
        bubble = QTextEdit()
        bubble.setReadOnly(True)
        bubble.setText(text)
        bubble.setMinimumWidth(200)
        bubble.setMaximumWidth(400)
        
        # Auto-adjust height based on content
        doc_height = bubble.document().size().height()
        bubble.setMinimumHeight(doc_height + 20)
        bubble.setMaximumHeight(doc_height + 20)
        
        # Style the bubble
        bubble.setStyleSheet(
            "QTextEdit {"
            "border-radius: 10px;"
            "padding: 10px;"
            f"background-color: {'#DCF8C6' if is_user else '#E8E8E8'};"
            "}"
        )
        
        # Create container for bubble and add margin
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addWidget(bubble)
        
        # Align messages to right for user, left for bot
        if is_user:
            layout.addStretch()
            layout.addWidget(bubble_container)
            layout.addWidget(icon_label)
        else:
            layout.addWidget(icon_label)
            layout.addWidget(bubble_container)
            layout.addStretch()
            
        self.setLayout(layout)

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
    
    # Save default icons if they don't exist
    if not os.path.exists('user_icon.png'):
        with open('user_icon.svg', 'w') as f:
            f.write(user_svg)
        # Convert SVG to PNG using Qt
        app = QApplication.instance() or QApplication([])
        icon = QIcon('user_icon.svg')
        pixmap = icon.pixmap(QSize(32, 32))
        pixmap.save('user_icon.png')
        os.remove('user_icon.svg')
        
    if not os.path.exists('bot_icon.png'):
        with open('bot_icon.svg', 'w') as f:
            f.write(bot_svg)
        # Convert SVG to PNG using Qt
        app = QApplication.instance() or QApplication([])
        icon = QIcon('bot_icon.svg')
        pixmap = icon.pixmap(QSize(32, 32))
        pixmap.save('bot_icon.png')
        os.remove('bot_icon.svg')

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
                # Get message from input queue
                message = self.input_queue.get(timeout=0.1)
                
                # Simulate bot processing (replace with actual bot logic)
                time.sleep(1)  # Simulate processing time
                response = f"Bot response to: {message}"
                
                # Send response through output queue
                self.output_queue.put(response)
                self.response_ready.emit(response)
                
            except queue.Empty:
                continue
                
    def stop(self):
        self.running = False

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Application")
        self.setMinimumSize(600, 400)
        
        # Create default icons if they don't exist
        create_default_icons()
        
        # Create queues for communication
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
        # Initialize UI
        self.init_ui()
        
        # Start worker thread
        self.worker = ChatWorker(self.input_queue, self.output_queue)
        self.worker.response_ready.connect(self.add_bot_message)
        self.worker.start()
        
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create widget to hold messages
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_widget)
        layout.addWidget(self.scroll_area)
        
        # Create input area
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)
        
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if message:
            # Add user message to chat
            self.add_user_message(message)
            
            # Clear input field
            self.message_input.clear()
            
            # Send message to worker thread
            self.input_queue.put(message)
            
    def add_user_message(self, message):
        self.add_message(message, is_user=True)
        
    def add_bot_message(self, message):
        self.add_message(message, is_user=False)
        
    def add_message(self, message, is_user=True):
        # Create and add message widget
        message_widget = MessageWidget(message, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
        
    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show window
    window = ChatWindow()
    window.show()
    
    sys.exit(app.exec_())
