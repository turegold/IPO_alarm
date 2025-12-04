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
        self.table.setColumnCount(8)   # 취소 버튼 포함
        self.table.setHorizontalHeaderLabels(
            ["종목명", "배정수량", "매수가", "매도가", "상장일", "수익", "수익률", "취소"]
        )
        layout.addWidget(self.table)

        # 종목명 칼럼 넓게
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(7, 70)

        self.setLayout(layout)

        # 첫 로딩
        self.load_completed()
        self.apply_filter()

        # 자동 계산 연결 (유저 입력에만 반응하도록, 실제 채우는 동안은 blockSignals 사용)
        self.table.itemChanged.connect(self.on_item_changed)

    # 🔥 탭 전환 시 refresh
    def refresh(self):
        self.table.itemChanged.disconnect(self.on_item_changed)
        self.load_completed()
        self.apply_filter()
        self.table.itemChanged.connect(self.on_item_changed)

    # ===========================================================
    # JSON 전체 로드 (self.all_items만 채움)
    # ===========================================================
    def load_completed(self):
        if not self.data_path.exists():
            self.all_items = []
            return

        with self.data_path.open("r", encoding="utf-8") as f:
            try:
                self.all_items = json.load(f)
            except Exception:
                self.all_items = []

    # ===========================================================
    # 상장일 문자열 → (year, month) 추출
    #  - "2025.12.10" → (2025, 12)
    #  - "12.10" 또는 빈 문자열 → (None, None)
    # ===========================================================
    def _extract_year_month(self, listing_str: str):
        if not listing_str:
            return None, None

        parts = listing_str.split(".")
        try:
            if len(parts) >= 3 and len(parts[0]) == 4:
                # "YYYY.MM.DD" 형태
                year = int(parts[0])
                month = int(parts[1])
                return year, month
        except Exception:
            pass
        return None, None

    # ===========================================================
    # 현재 선택된 년/월 기준으로 self.all_items를 필터링해서 테이블 채우기
    # ===========================================================
    def apply_filter(self):
        if not hasattr(self, "table"):
            return

        try:
            selected_year = int(self.year_box.currentText())
            selected_month = int(self.month_box.currentText())
        except Exception:
            selected_year, selected_month = None, None

        # 필터링
        filtered = []
        for item in self.all_items:
            y, m = self._extract_year_month(item.get("상장일", ""))

            if y is None:
                # 연도가 없는 예전 데이터는 어떤 년/월이든 항상 표시
                filtered.append(item)
            else:
                if y == selected_year and (m is None or m == selected_month):
                    filtered.append(item)

        # 테이블 채우기 (신호 잠깐 끄기)
        self.table.blockSignals(True)

        self.table.setRowCount(len(filtered))

        for row, item in enumerate(filtered):
            # 종목명 (읽기 전용)
            name_item = QTableWidgetItem(item.get("종목명", ""))
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            # 배정수량 (편집 가능)
            self.table.setItem(row, 1, QTableWidgetItem(item.get("배정수량", "")))

            # 매수가 (읽기 전용)
            buy_item = QTableWidgetItem(str(item.get("매수가", "")))
            buy_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 2, buy_item)

            # 매도가 (편집 가능)
            self.table.setItem(row, 3, QTableWidgetItem(item.get("매도가", "")))

            # 상장일 (읽기 전용)
            listing_item = QTableWidgetItem(item.get("상장일", ""))
            listing_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 4, listing_item)

            # 수익 (읽기 전용)
            profit_item = QTableWidgetItem("")
            profit_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 5, profit_item)

            # 수익률 (읽기 전용)
            rate_item = QTableWidgetItem("")
            rate_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 6, rate_item)

            # 수익/수익률 자동 계산
            self.calculate_row(row)

            # 각 행에 취소 버튼 추가
            cancel_btn = QPushButton("취소")
            cancel_btn.clicked.connect(lambda _, r=row: self.cancel_row(r))
            self.table.setCellWidget(row, 7, cancel_btn)

        self.table.blockSignals(False)

    # ===========================================================
    # 셀 변경 → 자동 계산 + 자동 저장
    # ===========================================================
    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col in (1, 3):  # 배정수량, 매도가
            self.calculate_row(row)
            self.save_all()

    # ===========================================================
    # 한 행 계산
    # ===========================================================
    def calculate_row(self, row):
        qty_item = self.table.item(row, 1)
        buy_item = self.table.item(row, 2)
        sell_item = self.table.item(row, 3)

        try:
            qty = int(qty_item.text()) if qty_item and qty_item.text() else 0
            buy = int(buy_item.text()) if buy_item and buy_item.text() else 0
            sell = int(sell_item.text()) if sell_item and sell_item.text() else 0
        except Exception:
            return

        if qty > 0 and buy > 0 and sell > 0:
            profit = (sell - buy) * qty
            rate = ((sell - buy) / buy) * 100
        else:
            profit = ""
            rate = ""

        # 수익 / 수익률은 읽기 전용 셀에 넣기
        profit_item = QTableWidgetItem(str(profit))
        profit_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 5, profit_item)

        rate_str = f"{rate:.2f}%" if rate != "" else ""
        rate_item = QTableWidgetItem(rate_str)
        rate_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 6, rate_item)

    # ===========================================================
    # 특정 행 ‘청약 취소’
    # ===========================================================
    def cancel_row(self, row):
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        name = name_item.text()

        # all_items에서 제거
        self.all_items = [c for c in self.all_items if c.get("종목명") != name]

        # JSON 저장
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(self.all_items, f, ensure_ascii=False, indent=2)

        print(f"[취소 완료] {name} 삭제됨")

        # 현재 필터 기준으로 다시 표시
        self.apply_filter()

    # ===========================================================
    # 저장 (현재 테이블의 변경 내용을 self.all_items에 반영 후 전체 저장)
    # ===========================================================
    def save_all(self):
        # 현재 필터 기준으로 화면에 보이는 행들을 dict로 수집
        visible_rows = {}
        total_rows = self.table.rowCount()
        for row in range(total_rows):
            name_item = self.table.item(row, 0)
            if not name_item:
                continue
            name = name_item.text()
            visible_rows[name] = {
                "종목명": name,
                "배정수량": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "매수가": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "매도가": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "상장일": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
            }

        # all_items에 반영
        new_all = []
        for item in self.all_items:
            name = item.get("종목명", "")
            if name in visible_rows:
                new_all.append(visible_rows[name])
            else:
                new_all.append(item)

        self.all_items = new_all

        # JSON으로 저장
        with self.data_path.open("w", encoding="utf-8") as f:
            json.dump(self.all_items, f, ensure_ascii=False, indent=2)

        print("[저장 완료] completed.json 업데이트됨")