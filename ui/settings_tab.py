from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.webhook_input = QLineEdit()
        layout.addRow("디스코드 웹훅 URL:", self.webhook_input)

        test_btn = QPushButton("웹훅 테스트 메시지 보내기")
        layout.addWidget(test_btn)

        self.setLayout(layout)