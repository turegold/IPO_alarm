# ui/result_tab.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from datetime import datetime
import json


class ResultTab(QWidget):
    def __init__(self):
        super().__init__()
        self.data_path = Path("data") / "completed.json"

        # completed.json 전체를 들고 있을 리스트
        self.all_items = []

        self.init_ui()

    # =========================================
    # UI 구성
    # =========================================
    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("청약 완료 종목 수익 입력")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ---------------------------
        # 년/월 선택 + 조회 버튼
        # ---------------------------
        ym_layout = QHBoxLayout()

        # 년도 선택
        self.year_box = QComboBox()
        current_year = datetime.now().year
        for y in [2023, 2024, 2025, 2026]:
            self.year_box.addItem(str(y))
        self.year_box.setCurrentText(str(current_year))
        ym_layout.addWidget(self.year_box)

        # 월 선택
        self.month_box = QComboBox()
        for m in range(1, 13):
            self.month_box.addItem(str(m))
        self.month_box.setCurrentText(str(datetime.now().month))
        ym_layout.addWidget(self.month_box)

        # 조회 버튼
        self.query_btn = QPushButton("조회")
        self.query_btn.clicked.connect(self.apply_filter)
        ym_layout.addWidget(self.query_btn)

        layout.addLayout(ym_layout)

        # ---------------------------
        # 테이블
        # ---------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(9)   # 취소 + 알림 버튼 포함
        self.table.setHorizontalHeaderLabels(
            ["종목명", "배정수량", "매수가", "매도가",
             "상장일", "수익", "수익률", "알림", "취소"]
        )
        layout.addWidget(self.table)

        # 종목명 칼럼 넓게
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 70)

        self.setLayout(layout)

        # 첫 로딩
        self.load_completed()
        self.apply_filter()

        # 자동 계산 연결
        self.table.itemChanged.connect(self.on_item_changed)

    # 🔥 탭 전환 시 refresh
    def refresh(self):
        self.table.itemChanged.disconnect(self.on_item_changed)
        self.load_completed()
        self.apply_filter()
        self.table.itemChanged.connect(self.on_item_changed)

    # ===========================================================
    # JSON 전체 로드
    # ===========================================================
    def load_completed(self):
        if not self.data_path.exists():
            self.all_items = []
            return

        with self.data_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []

            # 기존 데이터에 알림 필드가 없을 경우 기본값 추가
            for item in data:
                if "알림" not in item:
                    item["알림"] = True

            self.all_items = data

    # ===========================================================
    # 상장일에서 (연도, 월) 추출
    # ===========================================================
    def _extract_year_month(self, listing_str: str):
        if not listing_str:
            return None, None

        parts = listing_str.split(".")
        try:
            if len(parts) >= 3 and len(parts[0]) == 4:
                return int(parts[0]), int(parts[1])
        except:
            pass
        return None, None

    # ===========================================================
    # 화면 갱신
    # ===========================================================
    def apply_filter(self):
        if not hasattr(self, "table"):
            return

        try:
            selected_year = int(self.year_box.currentText())
            selected_month = int(self.month_box.currentText())
        except:
            selected_year = selected_month = None

        filtered = []
        for item in self.all_items:
            y, m = self._extract_year_month(item.get("상장일", ""))

            if y is None:
                filtered.append(item)
            else:
                if y == selected_year and (m is None or m == selected_month):
                    filtered.append(item)

        self.table.blockSignals(True)
        self.table.setRowCount(len(filtered))

        for row, item in enumerate(filtered):
            # 종목명
            name_item = QTableWidgetItem(item.get("종목명", ""))
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            # 배정수량
            self.table.setItem(row, 1, QTableWidgetItem(item.get("배정수량", "")))

            # 매수가
            buy_item = QTableWidgetItem(str(item.get("매수가", "")))
            buy_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 2, buy_item)

            # 매도가
            self.table.setItem(row, 3, QTableWidgetItem(item.get("매도가", "")))

            # 상장일
            listing_item = QTableWidgetItem(item.get("상장일", ""))
            listing_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 4, listing_item)

            # 수익/수익률
            self.table.setItem(row, 5, QTableWidgetItem(""))
            self.table.setItem(row, 6, QTableWidgetItem(""))
            self.calculate_row(row)

            # -----------------------------
            # 알림 버튼
            # -----------------------------
            alarm_btn = QPushButton("알림 ON" if item.get("알림", True) else "알림 OFF")
            alarm_btn.setCheckable(True)
            alarm_btn.setChecked(item.get("알림", True))

            alarm_btn.clicked.connect(lambda _, r=row: self.toggle_alarm(r))
            self.table.setCellWidget(row, 7, alarm_btn)

            # 취소 버튼
            cancel_btn = QPushButton("취소")
            cancel_btn.clicked.connect(lambda _, r=row: self.cancel_row(r))
            self.table.setCellWidget(row, 8, cancel_btn)

        self.table.blockSignals(False)

    # ===========================================================
    # 알림 토글
    # ===========================================================
    def toggle_alarm(self, row):
        name = self.table.item(row, 0).text()
        btn = self.table.cellWidget(row, 7)

        for item in self.all_items:
            if item["종목명"] == name:
                item["알림"] = btn.isChecked()

                btn.setText("알림 ON" if btn.isChecked() else "알림 OFF")
                break

        self.save_all()

    # ===========================================================
    # 셀 변경 -> 자동 계산 및 저장
    # ===========================================================
    def on_item_changed(self, item):
        if item.column() in (1, 3):
            self.calculate_row(item.row())
            self.save_all()

    # 계산
    def calculate_row(self, row):
        qty_item = self.table.item(row, 1)
        buy_item = self.table.item(row, 2)
        sell_item = self.table.item(row, 3)

        try:
            qty = int(qty_item.text() or 0)
            buy = int(buy_item.text() or 0)
            sell = int(sell_item.text() or 0)
        except:
            return

        if qty > 0 and buy > 0 and sell > 0:
            profit = (sell - buy) * qty
            rate = ((sell - buy) / buy) * 100
        else:
            profit = ""
            rate = ""

        p_item = QTableWidgetItem(str(profit))
        p_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 5, p_item)

        r_item = QTableWidgetItem(f"{rate:.2f}%" if rate != "" else "")
        r_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 6, r_item)

    # ===========================================================
    # 한 행 삭제
    # ===========================================================
    def cancel_row(self, row):
        name = self.table.item(row, 0).text()

        self.all_items = [item for item in self.all_items if item["종목명"] != name]

        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(self.all_items, f, ensure_ascii=False, indent=2)

        self.apply_filter()

    # ===========================================================
    # 전체 저장
    # ===========================================================
    def save_all(self):
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(self.all_items, f, ensure_ascii=False, indent=2)

        print("[저장 완료] completed.json 업데이트됨")