# 월별 공모주 일정을 크롤링해 조회하고, 상세 정보 확인, 청약 예정 등록, 청약 완료 처리까지 한 화면에서 관리하는 PyQt 기반 메인 일정 조회 UI 탭

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor, QMovie

from pathlib import Path
import json
from datetime import datetime

from services.ipo_loader import (
    load_ipo_list,
    load_completed_names,
    load_subscribe_names,
)
from services.subscribe_service import register_subscribe
from services.completed_service import mark_completed
from services.date_utils import parse_schedule, is_expired
from services.crawler import save_ipo_json
from services.detail_crawler import crawl_detail
from ui.detail_dialog import DetailDialog


# 월별 공모주 데이터를 백그라운드 스레드에서 크롤링하는 함수
class CrawlThread(QThread):
    finished = pyqtSignal(bool)

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


# 공모주 일정 조회 UI
class ScheduleTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_year = 2025
        self.selected_month = 12
        self.crawl_thread = None
        self.init_ui()

    # UI 구성
    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("공모주 일정 조회")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 년/월 선택
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

        # 로딩 스피너
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()

        self.movie = QMovie("ui/imgs/loading_spinner.gif")
        self.movie.setScaledSize(QSize(48, 48))
        self.loading_label.setMovie(self.movie)
        layout.addWidget(self.loading_label)

        # 테이블 생성
        self.table_schedule = QTableWidget()
        self.table_schedule.setColumnCount(7)
        self.table_schedule.setHorizontalHeaderLabels(
            ["종목명", "청약일", "상장일", "주관사", "자세히 보기", "청약 예정", "청약 완료"]
        )
        layout.addWidget(self.table_schedule)

        self.setLayout(layout)

        # 초기 자동 로딩
        QTimer.singleShot(100, self.start_query)

    # UI 입력 비활성화, 로딩 애니메이션 표시, 크롤링 스레드 시작을 하는 함수
    def start_query(self):
        self.query_btn.setEnabled(False)
        self.year_box.setEnabled(False)
        self.month_box.setEnabled(False)

        self.loading_label.show()
        self.movie.start()

        year = int(self.year_box.currentText())
        month = int(self.month_box.currentText())

        self.crawl_thread = CrawlThread(year, month)
        self.crawl_thread.finished.connect(self.finish_query)
        self.crawl_thread.start()

    # 크롤링 종료 후 UI를 복구하는 함수
    def finish_query(self, ok):
        self.movie.stop()
        self.loading_label.hide()

        self.query_btn.setEnabled(True)
        self.year_box.setEnabled(True)
        self.month_box.setEnabled(True)

        if ok:
            self.load_latest_data()

    # 로드된 데이터를 UI에 반영하는 함수
    def load_latest_data(self):
        year = int(self.year_box.currentText())
        month = int(self.month_box.currentText())

        items = load_ipo_list(year, month)
        completed_names = load_completed_names()
        subscribe_names = load_subscribe_names()

        self.table_schedule.setRowCount(len(items))

        for row, item in enumerate(items):
            self.table_schedule.setItem(row, 0, QTableWidgetItem(item["종목명"]))
            self.table_schedule.setItem(row, 1, QTableWidgetItem(item["공모일정"]))
            self.table_schedule.setItem(row, 2, QTableWidgetItem(item["상장일"]))
            self.table_schedule.setItem(row, 3, QTableWidgetItem(item["주간사"]))

            # 자세히 보기
            btn_detail = QPushButton("보기")
            btn_detail.clicked.connect(lambda _, data=item: self.open_detail(data))
            self.table_schedule.setCellWidget(row, 4, btn_detail)


            # 청약 예정 버튼
            btn_sub = QPushButton()
            if item["종목명"] in subscribe_names:
                btn_sub.setText("등록됨")
                btn_sub.setEnabled(False)
            elif item["종목명"] in completed_names:
                btn_sub.setText("불가")
                btn_sub.setEnabled(True)
                btn_sub.clicked.connect(lambda _, data=item: self.warn_already_completed())
            else:
                btn_sub.setText("등록")
                btn_sub.clicked.connect(
                    lambda _, data=item: self.click_subscribe(data)
                )
            self.table_schedule.setCellWidget(row, 5, btn_sub)


            # 청약 완료 버튼
            btn_done = QPushButton()
            if item["종목명"] in completed_names:
                btn_done.setText("완료됨")
                btn_done.setEnabled(False)
            else:
                btn_done.setText("완료")
                btn_done.clicked.connect(
                    lambda _, data=item: self.click_completed(data)
                )
            self.table_schedule.setCellWidget(row, 6, btn_done)

            # 테이블 색상 적용
            self.apply_row_style(row, item["공모일정"], year)


    # 공모주 일정 기준으로 행 색상을 지정하는 함수
    # 지난 공모주: 빨간색 배경
    # 진행 중인 공모주: 초록색 배경
    # 예정 공모주: 흰 배경
    def apply_row_style(self, row, schedule: str, year: int):
        start, end = parse_schedule(schedule, year)

        bg = QColor("white")
        if is_expired(start, end):
            bg = QColor("#FFB3B3")      # 지난 공모주
        elif start and datetime.now().date() >= start.date():
            bg = QColor("#C4F0C4")      # 진행 중

        for col in range(4):  # 텍스트가 있는 4개 컬럼만 색칠
            item = self.table_schedule.item(row, col)
            if item:
                item.setBackground(bg)


    # 종목 상세 URL을 크롤링하는 함수
    def open_detail(self, item: dict):
        detail_url = item.get("상세URL")
        if detail_url:
            try:
                detail = crawl_detail(detail_url)
                detail["종목명"] = item["종목명"]
            except Exception:
                detail = {"종목명": item["종목명"]}
        else:
            detail = {"종목명": item["종목명"]}

        dialog = DetailDialog(detail, self)
        dialog.exec()


    # 공모주를 청약 예정 목록에 등록하는 함수
    def click_subscribe(self, item: dict):
        year = int(self.year_box.currentText())

        success, message = register_subscribe(item, year)

        if success:
            QMessageBox.information(self, "등록 완료", message)
        else:
            QMessageBox.warning(self, "등록 실패", message)

        self.load_latest_data()

    # 이미 완료한 공모주인데 예정을 누른 경우, 경고 메시지를 표시하는 함수
    def warn_already_completed(self):
        QMessageBox.warning(self, "안내", "이미 청약 완료한 공모주입니다.")


    # 청약 완료 처리를 하는 함수
    def click_completed(self, item: dict):
        year = int(self.year_box.currentText())

        success, message = mark_completed(item, year)

        if success:
            QMessageBox.information(self, "청약 완료", message)
        else:
            QMessageBox.warning(self, "등록 실패", message)

        self.load_latest_data()