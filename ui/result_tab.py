from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout,
    QLineEdit, QPushButton, QTableWidget
)
from PyQt6.QtCore import Qt


class ResultTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("청약 완료 종목 수익 입력")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()

        self.input_name = QLineEdit()
        self.input_qty = QLineEdit()
        self.input_buy = QLineEdit()
        self.input_sell = QLineEdit()

        form.addRow("종목명:", self.input_name)
        form.addRow("배정 수량:", self.input_qty)
        form.addRow("매수가:", self.input_buy)
        form.addRow("매도가:", self.input_sell)

        layout.addLayout(form)

        save_btn = QPushButton("수익 계산 및 저장")
        layout.addWidget(save_btn)

        self.table_profit = QTableWidget()
        self.table_profit.setColumnCount(6)
        self.table_profit.setHorizontalHeaderLabels(
            ["종목", "수량", "매수가", "매도가", "수익", "수익률"]
        )
        layout.addWidget(self.table_profit)

        self.setLayout(layout)