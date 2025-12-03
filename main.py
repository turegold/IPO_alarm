import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QLineEdit, QFormLayout, QTextEdit
)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("공모주 일정·수익 분석 자동화 시스템")
        self.resize(900, 600)

        # 메인 탭
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 탭 생성
        self.tab_schedule = QWidget()
        self.tab_result = QWidget()
        self.tab_analysis = QWidget()
        self.tab_settings = QWidget()

        # 탭 추가
        self.tabs.addTab(self.tab_schedule, "공모주 일정")
        self.tabs.addTab(self.tab_result, "청약 완료 / 수익 입력")
        self.tabs.addTab(self.tab_analysis, "월별 수익 분석")
        self.tabs.addTab(self.tab_settings, "설정")

        # 각 탭 UI 초기화
        self.init_schedule_tab()
        self.init_result_tab()
        self.init_analysis_tab()
        self.init_settings_tab()

    # ---------------------------
    # 1. 공모주 일정 탭
    # ---------------------------
    def init_schedule_tab(self):
        layout = QVBoxLayout()

        title = QLabel("공모주 일정 조회")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 업데이트 버튼
        update_btn = QPushButton("데이터 업데이트 (크롤링)")
        layout.addWidget(update_btn)

        # 테이블 (공모주 목록)
        self.table_schedule = QTableWidget()
        self.table_schedule.setColumnCount(4)
        self.table_schedule.setHorizontalHeaderLabels(["종목명", "청약일", "상장일", "주관사"])
        layout.addWidget(self.table_schedule)

        self.tab_schedule.setLayout(layout)

    # ---------------------------
    # 2. 청약 완료 / 수익 입력 탭
    # ---------------------------
    def init_result_tab(self):
        layout = QVBoxLayout()

        title = QLabel("청약 완료 종목 수익 입력")
        title.setAlignment(Qt.AlignCenter)
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

        # 수익 결과 테이블
        self.table_profit = QTableWidget()
        self.table_profit.setColumnCount(6)
        self.table_profit.setHorizontalHeaderLabels(["종목", "수량", "매수가", "매도가", "수익", "수익률"])
        layout.addWidget(self.table_profit)

        self.tab_result.setLayout(layout)

    # ---------------------------
    # 3. 월별 수익 분석 탭
    # ---------------------------
    def init_analysis_tab(self):
        layout = QVBoxLayout()

        title = QLabel("월별 수익 분석")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 분석 버튼
        analyse_btn = QPushButton("월별 분석 실행")
        layout.addWidget(analyse_btn)

        # 분석 결과 표시
        self.analysis_text = QTextEdit()
        self.analysis_text.setPlaceholderText("월별 수익 분석 결과가 여기에 표시됩니다.")
        layout.addWidget(self.analysis_text)

        self.tab_analysis.setLayout(layout)

    # ---------------------------
    # 4. 설정 탭
    # ---------------------------
    def init_settings_tab(self):
        layout = QFormLayout()

        self.webhook_input = QLineEdit()
        layout.addRow("디스코드 웹훅 URL:", self.webhook_input)

        test_btn = QPushButton("웹훅 테스트 메시지 보내기")
        layout.addWidget(test_btn)

        self.tab_settings.setLayout(layout)


# ---------------------------
# 프로그램 실행
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())