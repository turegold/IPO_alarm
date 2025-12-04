# ui/schedule_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QMovie

from pathlib import Path
import json
from datetime import datetime

from services.crawler import save_ipo_json
from services.detail_crawler import crawl_detail
from ui.detail_dialog import DetailDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize

# ==========================
# ✔ 크롤링을 위한 백그라운드 스레드
# ==========================
class CrawlThread(QThread):
    finished = pyqtSignal(bool)  # 성공 여부 반환

    def __init__(self, year, month):
        super().__init__()
        self.year = year
        self.month = month

    def run(self):
        try:
            save_ipo_json(self.year, self.month)
            self.finished.emit(True)
        except Exception:
            self.finished.emit(False)


# ==========================
# ✔ 메인 UI
# ==========================
class ScheduleTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_year = 2025
        self.selected_month = 12
        self.crawl_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ---------------------------
        # 제목
        # ---------------------------
        title = QLabel("공모주 일정 조회")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ---------------------------
        # 년/월 선택 영역
        # ---------------------------
        ym_layout = QHBoxLayout()

        self.year_box = QComboBox()
        for y in [2023, 2024, 2025, 2026]:
            self.year_box.addItem(str(y))
        self.year_box.setCurrentText(str(self.selected_year))
        ym_layout.addWidget(self.year_box)

        self.month_box = QComboBox()
        for m in range(1, 13):
            self.month_box.addItem(str(m))
        self.month_box.setCurrentText(str(self.selected_month))
        ym_layout.addWidget(self.month_box)

        # 조회 버튼
        self.query_btn = QPushButton("조회")
        self.query_btn.clicked.connect(self.start_query)
        ym_layout.addWidget(self.query_btn)

        layout.addLayout(ym_layout)

        # ---------------------------
        # 로딩 스피너 (GIF)
        # ---------------------------
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()

        self.movie = QMovie("ui/imgs/loading_spinner.gif")
        self.movie.setScaledSize(QSize(48, 48))
        self.loading_label.setMovie(self.movie)

        layout.addWidget(self.loading_label)

        # ---------------------------
        # 테이블
        # ---------------------------
        self.table_schedule = QTableWidget()
        self.table_schedule.setColumnCount(5)
        self.table_schedule.setHorizontalHeaderLabels(
            ["종목명", "청약일", "상장일", "주관사", "자세히 보기"]
        )
        layout.addWidget(self.table_schedule)

        self.setLayout(layout)

        # 첫 로딩은 UI를 띄운 뒤 자동 실행하도록 처리
        QTimer.singleShot(100, self.start_query)

    # ---------------------------
    # 조회 버튼 → 스레드 실행
    # ---------------------------
    def start_query(self):
        # UI 비활성화
        self.query_btn.setEnabled(False)
        self.year_box.setEnabled(False)
        self.month_box.setEnabled(False)

        # 스피너 실행
        self.loading_label.show()
        self.movie.start()

        year = int(self.year_box.currentText())
        month = int(self.month_box.currentText())

        self.crawl_thread = CrawlThread(year, month)
        self.crawl_thread.finished.connect(self.finish_query)
        self.crawl_thread.start()

    # ---------------------------
    # 스레드 종료 시 실행
    # ---------------------------
    def finish_query(self, ok):
        # 스피너 종료
        self.movie.stop()
        self.loading_label.hide()

        # UI 활성화
        self.query_btn.setEnabled(True)
        self.year_box.setEnabled(True)
        self.month_box.setEnabled(True)

        if ok:
            self.load_latest_data()
        else:
            print("크롤링 실패")

    # ---------------------------
    # JSON 로드 → 테이블 채우기
    # ---------------------------
    def load_latest_data(self):
        year = int(self.year_box.currentText())
        month = int(self.month_box.currentText())

        data_path = Path("data") / f"ipo_{year}_{month:02d}.json"
        if not data_path.exists():
            print("데이터 없음")
            return

        with data_path.open("r", encoding="utf-8") as f:
            items = json.load(f)

        self.table_schedule.setRowCount(len(items))

        for row, item in enumerate(items):
            self.table_schedule.setItem(row, 0, QTableWidgetItem(item["종목명"]))
            self.table_schedule.setItem(row, 1, QTableWidgetItem(item["공모일정"]))
            self.table_schedule.setItem(row, 2, QTableWidgetItem(item["상장일"]))
            self.table_schedule.setItem(row, 3, QTableWidgetItem(item["주간사"]))

            btn = QPushButton("보기")
            btn.clicked.connect(lambda _, data=item: self.open_detail(data))
            self.table_schedule.setCellWidget(row, 4, btn)

            self.apply_row_style(row, item["공모일정"])

    # ---------------------------
    # 공모 일정 파싱
    # ---------------------------
    def parse_schedule(self, schedule):
        try:
            s, e = schedule.split("~")
            s = s.strip().replace(".", "-")
            e = e.strip().replace(".", "-")
            year = int(self.year_box.currentText())
            start = datetime.strptime(f"{year}-{s}", "%Y-%m-%d")
            end = datetime.strptime(f"{year}-{e}", "%Y-%m-%d")
            return start, end
        except:
            return None, None

    # ---------------------------
    # 색상 적용
    # ---------------------------
    def apply_row_style(self, row, schedule):
        start, end = self.parse_schedule(schedule)
        if not start:
            return

        now = datetime.now()

        expired = False
        if now.date() > end.date():
            expired = True
        elif now.date() == end.date() and now.hour >= 16:
            expired = True

        if expired:
            bg = QColor("#FFB3B3")
        elif now.date() >= start.date():
            bg = QColor("#C4F0C4")
        else:
            bg = QColor("white")

        for col in range(4):
            item = self.table_schedule.item(row, col)
            if item:
                item.setBackground(bg)

    # ---------------------------
    # 상세 보기
    # ---------------------------
    def open_detail(self, item):
        detail_url = item.get("상세URL")
        if not detail_url:
            data = {"종목명": item["종목명"], "업종": "", "logo": None,
                    "공모가격": {}, "공모주식수": [], "증권사배정": []}
        else:
            try:
                data = crawl_detail(detail_url)
            except:
                data = {"종목명": item["종목명"], "업종": "", "logo": None,
                        "공모가격": {}, "공모주식수": [], "증권사배정": []}

            data["종목명"] = item["종목명"]

        dialog = DetailDialog(data, self)
        dialog.exec()