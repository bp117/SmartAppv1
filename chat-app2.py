import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QDateTime
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont
import queue
import time
import os

# ... [Previous LoadingDots, MessageBubble, and MessageWidget classes remain the same] ...

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
        
        # Scroll area setup remains the same
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
        
        # Create a container widget for input area
        input_container = QWidget()
        input_container.setStyleSheet(
            "QWidget {"
            "background-color: white;"
            "border: 1px solid #b4a7d6;"
            "border-radius: 5px;"
            "}"
        )
        
        # Create layout for input container
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(0)
        
        # Create and style the message input
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet(
            "QTextEdit {"
            "border: none;"
            "padding: 5px;"
            "background-color: transparent;"
            "}"
        )
        
        # Create and style the send button
        send_button = QPushButton("Send")
        send_button.setFixedSize(60, 30)
        send_button.setStyleSheet(
            "QPushButton {"
            "background-color: #b4a7d6;"
            "color: white;"
            "border: none;"
            "border-radius: 15px;"
            "margin: 5px;"
            "}"
            "QPushButton:hover {"
            "background-color: #9982c7;"
            "}"
        )
        send_button.clicked.connect(self.send_message)
        
        # Add widgets to input layout
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        
        # Add input container to main layout
        layout.addWidget(input_container)
        
        self.message_input.installEventFilter(self)

    # ... [Rest of the ChatWindow methods remain the same] ...