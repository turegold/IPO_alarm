# ui/schedule_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor, QMovie

from pathlib import Path
import json
from datetime import datetime

from services.crawler import save_ipo_json
from services.detail_crawler import crawl_detail
from ui.detail_dialog import DetailDialog


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
        # 0:종목명, 1:청약일, 2:상장일, 3:주관사, 4:자세히 보기, 5:청약 완료
        self.table_schedule.setColumnCount(6)
        self.table_schedule.setHorizontalHeaderLabels(
            ["종목명", "청약일", "상장일", "주관사", "자세히 보기", "청약 완료"]
        )
        layout.addWidget(self.table_schedule)

        self.setLayout(layout)

        # 첫 로딩은 UI를 띄운 뒤 자동 실행
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

        # 이미 완료된 종목 목록 로드
        completed_path = Path("data") / "completed.json"
        if completed_path.exists():
            with completed_path.open("r", encoding="utf-8") as f:
                try:
                    completed_list = json.load(f)
                except Exception:
                    completed_list = []
        else:
            completed_list = []

        completed_names = {c.get("종목명") for c in completed_list}

        self.table_schedule.setRowCount(len(items))

        for row, item in enumerate(items):
            self.table_schedule.setItem(row, 0, QTableWidgetItem(item["종목명"]))
            self.table_schedule.setItem(row, 1, QTableWidgetItem(item["공모일정"]))
            self.table_schedule.setItem(row, 2, QTableWidgetItem(item["상장일"]))
            self.table_schedule.setItem(row, 3, QTableWidgetItem(item["주간사"]))

            # 자세히 보기 버튼
            view_btn = QPushButton("보기")
            view_btn.clicked.connect(lambda _, data=item: self.open_detail(data))
            self.table_schedule.setCellWidget(row, 4, view_btn)

            # 청약 완료 버튼
            done_btn = QPushButton()
            if item["종목명"] in completed_names:
                done_btn.setText("완료됨")
                done_btn.setEnabled(False)
            else:
                done_btn.setText("완료")
                done_btn.clicked.connect(
                    lambda _, data=item: self.mark_completed(data)
                )
            self.table_schedule.setCellWidget(row, 5, done_btn)

            # 행 색상 적용
            self.apply_row_style(row, item["공모일정"])

    # ---------------------------
    # 공모 일정 파싱
    # ---------------------------
    def parse_schedule(self, schedule: str):
        try:
            s, e = schedule.split("~")
            s = s.strip().replace(".", "-")
            e = e.strip().replace(".", "-")
            year = int(self.year_box.currentText())
            start = datetime.strptime(f"{year}-{s}", "%Y-%m-%d")
            end = datetime.strptime(f"{year}-{e}", "%Y-%m-%d")
            return start, end
        except Exception:
            return None, None

    # ---------------------------
    # 색상 적용
    # ---------------------------
    def apply_row_style(self, row, schedule: str):
        start, end = self.parse_schedule(schedule)
        if not start or not end:
            return

        now = datetime.now()

        expired = False
        if now.date() > end.date():
            expired = True
        elif now.date() == end.date() and now.hour >= 16:
            expired = True

        if expired:
            bg = QColor("#FFB3B3")  # 종료: 빨간색
        elif now.date() >= start.date():
            bg = QColor("#C4F0C4")  # 진행 중: 초록색
        else:
            bg = QColor("white")    # 아직 시작 전

        # 0~3열만 색 적용 (버튼 열 제외)
        for col in range(4):
            item = self.table_schedule.item(row, col)
            if item:
                item.setBackground(bg)

    # ---------------------------
    # 상세 보기
    # ---------------------------
    def open_detail(self, item: dict):
        detail_url = item.get("상세URL")
        if not detail_url:
            data = {
                "종목명": item["종목명"],
                "업종": "",
                "logo": None,
                "공모가격": {},
                "공모주식수": [],
                "증권사배정": [],
            }
        else:
            try:
                data = crawl_detail(detail_url)
            except Exception:
                data = {
                    "종목명": item["종목명"],
                    "업종": "",
                    "logo": None,
                    "공모가격": {},
                    "공모주식수": [],
                    "증권사배정": [],
                }
            else:
                data["종목명"] = item["종목명"]

        dialog = DetailDialog(data, self)
        dialog.exec()

    # ---------------------------
    # 청약 완료 처리
    # ---------------------------
    def mark_completed(self, item: dict):
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        file_path = data_dir / "completed.json"

        # 기존 데이터 로드
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                try:
                    completed = json.load(f)
                except Exception:
                    completed = []
        else:
            completed = []

        # 중복 체크
        for c in completed:
            if c.get("종목명") == item["종목명"]:
                print("[청약 완료] 이미 저장된 종목:", item["종목명"])
                return

        # 상세 페이지에서 확정 공모가 가져오기
        확정공모가 = None
        detail = {}
        if item.get("상세URL"):
            try:
                detail = crawl_detail(item["상세URL"])
            except Exception:
                detail = {}

        price_info = detail.get("공모가격", {})
        if "(확정)공모가격" in price_info:
            try:
                price_str = price_info["(확정)공모가격"]
                확정공모가 = int(
                    price_str.replace("원", "").replace(",", "").strip()
                )
            except Exception:
                확정공모가 = None

        # -------------------------------
        # ★ 연도를 포함한 상장일 생성
        # -------------------------------
        raw_listing = item.get("상장일", "")  # 예: "12.12"
        if raw_listing:
            year = int(self.year_box.currentText())
            fixed_listing = f"{year}.{raw_listing}"
        else:
            fixed_listing = ""

        new_entry = {
            "종목명": item["종목명"],
            "상장일": fixed_listing,
            "배정수량": "",
            "매수가": 확정공모가 if 확정공모가 else "",
            "매도가": "",
            "상세URL": item.get("상세URL", ""),
        }

        completed.append(new_entry)

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(completed, f, ensure_ascii=False, indent=2)

        print(f"[청약 완료 저장됨] {item['종목명']}")

        self.load_latest_data()