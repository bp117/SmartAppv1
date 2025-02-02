import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLabel,
    QScrollArea, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QPainter, QTextOption
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from queue import Queue
import threading

# Mock LangGraph setup (replace with your actual LangGraph logic)
class LangGraphChat:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
        self.agent = initialize_agent([], self.llm, agent="conversational-react-description", verbose=True)
        self.message_queue = Queue()

    def send_message(self, user_input):
        # Simulate sending a message to the bot
        def process():
            response = self.agent.run(user_input)
            self.message_queue.put(response)

        threading.Thread(target=process).start()

    def get_response(self):
        # Retrieve the bot's response from the queue
        if not self.message_queue.empty():
            return self.message_queue.get()
        return None


class ChatBubble(QFrame):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.text = text
        self.is_user = is_user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel(self.text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setFont(QFont("Arial", 12))

        if self.is_user:
            label.setStyleSheet("""
                background-color: #DCF8C6;
                padding: 10px;
                border-radius: 10px;
                max-width: 70%;
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            label.setStyleSheet("""
                background-color: #ECECEC;
                padding: 1px;
                border-radius: 10px;
                max-width: 70%;
            """)
            layout.setAlignment(Qt.AlignLeft)

        layout.addWidget(label)
        self.setLayout(layout)


class ChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang_graph_chat = LangGraphChat()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat Interface")
        self.setGeometry(100, 100, 400, 600)

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Scroll area for chat history
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Input area
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(60)
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.setAcceptRichText(False)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # Timer to check for bot responses
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_bot_response)
        self.timer.start(1000)  # Check every second

    def send_message(self):
        user_input = self.input_box.toPlainText().strip()
        if user_input:
            self.add_message(user_input, is_user=True)
            self.input_box.clear()
            self.lang_graph_chat.send_message(user_input)

    def add_message(self, text, is_user=False):
        bubble = ChatBubble(text, is_user)
        self.scroll_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def check_bot_response(self):
        response = self.lang_graph_chat.get_response()
        if response:
            self.add_message(response, is_user=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())
