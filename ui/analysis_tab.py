from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt


class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("월별 수익 분석")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        analyse_btn = QPushButton("월별 분석 실행")
        layout.addWidget(analyse_btn)

        self.analysis_text = QTextEdit()
        self.analysis_text.setPlaceholderText("월별 수익 분석 결과가 여기에 표시됩니다.")
        layout.addWidget(self.analysis_text)

        self.setLayout(layout)