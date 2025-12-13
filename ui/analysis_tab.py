# 청약 완료된 공모주 데이터를 기반으로 연도별 수익,수익률을 분석하고
# 결과를 테이블로 표시하며 CSV,PDF로 저장할 수 있는 PyQt 분석 UI 탭

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt
from pathlib import Path
from datetime import datetime
import json

from services.save_file import save_csv, save_pdf

# 공모주 월별 수익 분석 화면을 담당하는 클래스
class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()

        self.data_path = Path("data") / "completed.json"

        self.all_items = []
        self.current_profit = [0] * 12
        self.current_rate = [0] * 12
        self.monthly_items = [[] for _ in range(12)]
        self.monthly_qty_total = [0] * 12

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("월별 수익 분석")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 연도 선택
        ym = QHBoxLayout()
        self.year_box = QComboBox()
        for y in [2023, 2024, 2025, 2026]:
            self.year_box.addItem(str(y))
        self.year_box.setCurrentText(str(datetime.now().year))
        ym.addWidget(self.year_box)

        query_btn = QPushButton("조회")
        query_btn.clicked.connect(self.run_analysis)
        ym.addWidget(query_btn)
        layout.addLayout(ym)

        # 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["월", "총 수익", "평균 수익률(%)", "종목 수"])
        self.table.setRowCount(12)

        for i in range(12):
            self.table.setItem(i, 0, QTableWidgetItem(f"{i+1}월"))

        layout.addWidget(self.table)

        # 저장 버튼
        save_layout = QHBoxLayout()

        csv_btn = QPushButton("CSV로 저장")
        csv_btn.clicked.connect(self.handle_save_csv)
        save_layout.addWidget(csv_btn)

        pdf_btn = QPushButton("PDF로 저장")
        pdf_btn.clicked.connect(self.handle_save_pdf)
        save_layout.addWidget(pdf_btn)

        layout.addLayout(save_layout)
        self.setLayout(layout)

        self.run_analysis()


    # CSV 저장
    def handle_save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "CSV 저장", "", "CSV (*.csv)")
        if path:
            save_csv(path, self.table)

    # PDF 저장
    def handle_save_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF 저장", "", "PDF (*.pdf)")
        if path:
            save_pdf(
                path,
                self.year_box.currentText(),
                self.table,
                self.monthly_items,
                self.current_profit,
                self.current_rate,
                self.monthly_qty_total
            )

    # completed.json 파일을 로드하여 분석 대상 전체 종목 데이터를 메모리에 저장하는 함수
    def load_json(self):
        if not self.data_path.exists():
            self.all_items = []
            return
        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                self.all_items = json.load(f)
        except:
            self.all_items = []

    # 문자열을 파싱하여 연도/월로 분리하여 반환하는 함수
    def parse_listing(self, listing):
        try:
            y, m, _ = listing.split(".")
            return int(y), int(m)
        except:
            return None, None

    # 선택한 연도를 기준으로 종목 필터링, 수익,수익률 계산, 월별 통계 집계하고,
    # 계산 결과를 테이블에 표시, PDF/CSV 저장용 내부 데이터로 저장하는 함수
    def run_analysis(self):
        self.load_json()

        year_selected = int(self.year_box.currentText())

        monthly_profit = [0] * 12
        monthly_rates = [[] for _ in range(12)]
        monthly_count = [0] * 12
        monthly_items = [[] for _ in range(12)]
        monthly_qty_total = [0] * 12

        for item in self.all_items:
            year, month = self.parse_listing(item.get("상장일", ""))
            if year != year_selected or not month:
                continue

            idx = month - 1

            qty_raw = item.get("배정수량", "")
            buy_raw = item.get("매수가", "")
            sell_raw = item.get("매도가", "")

            # 빈 값 제거
            if not qty_raw or not buy_raw or not sell_raw:
                continue

            try:
                qty = int(qty_raw)
                buy = int(buy_raw)
                sell = int(sell_raw)
            except ValueError:
                continue

            if qty <= 0 or buy <= 0 or sell <= 0:
                continue

            profit = (sell - buy) * qty
            rate = (sell - buy) / buy * 100

            monthly_profit[idx] += profit
            monthly_rates[idx].append(rate)
            monthly_count[idx] += 1
            monthly_qty_total[idx] += qty

            monthly_items[idx].append(
                {
                    "name": item.get("종목명", ""),
                    "buy": buy,
                    "sell": sell,
                    "qty": qty,
                    "profit": profit,
                    "rate": rate,
                }
            )

        # UI 업데이트
        for i in range(12):
            avg_rate = sum(monthly_rates[i]) / len(monthly_rates[i]) if monthly_rates[i] else 0
            self.table.setItem(i, 1, QTableWidgetItem(f"{monthly_profit[i]:,}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{avg_rate:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(str(monthly_count[i])))

        self.current_profit = monthly_profit
        self.current_rate = [(sum(lst) / len(lst) if lst else 0) for lst in monthly_rates]
        self.monthly_items = monthly_items
        self.monthly_qty_total = monthly_qty_total