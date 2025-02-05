from PyQt5.QtCore import QEvent

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Application")

        # Set initial position and size
        self.setGeometry(50, 50, 600, 400)  

        create_default_icons()

        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        self.init_ui()

        self.worker = ChatWorker(self.input_queue, self.output_queue)
        self.worker.response_ready.connect(self.handle_bot_response)
        self.worker.start()

        self.loading_dots = None

    def event(self, event):
        # Handle minimize and restore events
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() == Qt.WindowMinimized:
                print("Window minimized")  # Debugging
            else:
                print("Window restored, triggering resize event")
                self.resizeEvent(event)  # Force resize event when restored
        
        return super().event(event)


from PyQt5.QtWidgets import QLineEdit, QFrame
from PyQt5.QtGui import QPixmap

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
    self.messages_widget.setStyleSheet("background-color: white;")

    self.scroll_area.setWidget(self.messages_widget)
    layout.addWidget(self.scroll_area)

    # Create an input frame to wrap text input and button
    input_frame = QFrame()
    input_frame.setStyleSheet(
        "QFrame {"
        "border: 1px solid #b4a7d6;"
        "border-radius: 5px;"
        "background-color: white;"
        "}"
    )
    input_frame_layout = QHBoxLayout(input_frame)
    input_frame_layout.setContentsMargins(10, 5, 10, 5)

    # Text input
    self.message_input = QLineEdit()
    self.message_input.setPlaceholderText("Type a message...")
    self.message_input.setStyleSheet(
        "QLineEdit {"
        "border: none;"
        "font-size: 14px;"
        "padding: 8px;"
        "color: #202124;"
        "}"
    )

    # Send button (inside the text field)
    self.send_button = QPushButton()
    self.send_button.setIcon(QIcon(QPixmap("send_icon.png")))  # Load a plane icon
    self.send_button.setFixedSize(32, 32)
    self.send_button.setStyleSheet(
        "QPushButton {"
        "border: none;"
        "background: transparent;"
        "padding: 0px;"
        "}"
    )
    self.send_button.clicked.connect(self.send_message)

    input_frame_layout.addWidget(self.message_input)
    input_frame_layout.addWidget(self.send_button)
    
    layout.addWidget(input_frame)
