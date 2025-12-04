from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from datetime import datetime
import csv
import json
import tempfile  # ← Windows 안전 이미지 경로용

import matplotlib.pyplot as plt
plt.style.use("ggplot")

from matplotlib import font_manager, rc
from fpdf import FPDF

# -------------------------------------------------------
# 프로젝트 절대경로 처리
# -------------------------------------------------------
CURRENT_DIR = Path(__file__).resolve().parent      # /Project/ui
PROJECT_ROOT = CURRENT_DIR.parent                 # /Project

DATA_DIR = PROJECT_ROOT / "data"
FONT_PATH = DATA_DIR / "fonts" / "Noto_Sans_KR" / "NotoSansKR-VariableFont_wght.ttf"

# -------------------------------------------------------
# Matplotlib 폰트 설정 (그래프용)
# -------------------------------------------------------
if FONT_PATH.exists():
    font_manager.fontManager.addfont(str(FONT_PATH))
    rc("font", family="Noto Sans KR")
    print("[OK] Matplotlib 한글 폰트 적용:", FONT_PATH)
else:
    print("[WARN] 그래프용 한국어 폰트를 찾지 못했습니다.")


# -------------------------------------------------------
# PDF용 폰트 절대경로 반환 함수
# -------------------------------------------------------
def get_korean_font_path():
    if FONT_PATH.exists():
        return str(FONT_PATH)
    return None


# -------------------------------------------------------
# 분석 탭 UI
# -------------------------------------------------------
class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()

        self.data_path = DATA_DIR / "completed.json"
        DATA_DIR.mkdir(exist_ok=True)

        # 이미지 저장을 OS 임시폴더로 전환 (Windows 문제 해결)
        self.temp_dir = Path(tempfile.gettempdir())

        self.all_items = []
        self.current_profit = [0] * 12
        self.current_rate = [0] * 12
        self.monthly_items = [[] for _ in range(12)]

        self.init_ui()

    # -------------------------------------------------------
    # UI 구성
    # -------------------------------------------------------
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
        csv_btn.clicked.connect(self.save_csv)
        save_layout.addWidget(csv_btn)

        pdf_btn = QPushButton("PDF로 저장")
        pdf_btn.clicked.connect(self.save_pdf)
        save_layout.addWidget(pdf_btn)

        layout.addLayout(save_layout)
        self.setLayout(layout)

        self.run_analysis()

    # -------------------------------------------------------
    # JSON 로드
    # -------------------------------------------------------
    def load_json(self):
        if not self.data_path.exists():
            self.all_items = []
            return

        try:
            with self.data_path.open("r", encoding="utf-8") as f:
                self.all_items = json.load(f)
        except:
            self.all_items = []

    # -------------------------------------------------------
    # 상장일 → (년, 월)
    # -------------------------------------------------------
    def parse_listing(self, listing):
        try:
            y, m, _ = listing.split(".")
            return int(y), int(m)
        except:
            return None, None

    # -------------------------------------------------------
    # 분석 실행
    # -------------------------------------------------------
    def run_analysis(self):
        self.load_json()

        year_selected = int(self.year_box.currentText())

        monthly_profit = [0] * 12
        monthly_rates = [[] for _ in range(12)]
        monthly_count = [0] * 12
        monthly_items = [[] for _ in range(12)]

        for item in self.all_items:
            year, month = self.parse_listing(item.get("상장일", ""))
            if year != year_selected or not month:
                continue

            idx = month - 1
            monthly_items[idx].append(item.get("종목명", ""))

            try:
                qty = int(item.get("배정수량", 0))
                buy = int(item.get("매수가", 0))
                sell = int(item.get("매도가", 0))
            except:
                continue

            if qty > 0 and buy > 0 and sell > 0:
                profit = (sell - buy) * qty
                rate = (sell - buy) / buy * 100

                monthly_profit[idx] += profit
                monthly_rates[idx].append(rate)
                monthly_count[idx] += 1

        # 테이블 채우기
        for i in range(12):
            avg_rate = sum(monthly_rates[i]) / len(monthly_rates[i]) if monthly_rates[i] else 0

            self.table.setItem(i, 1, QTableWidgetItem(f"{monthly_profit[i]:,}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{avg_rate:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(str(monthly_count[i])))

        self.current_profit = monthly_profit
        self.current_rate = [
            sum(lst)/len(lst) if lst else 0 for lst in monthly_rates
        ]
        self.monthly_items = monthly_items

    # -------------------------------------------------------
    # CSV 저장
    # -------------------------------------------------------
    def save_csv(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "CSV 저장", "", "CSV (*.csv)")
        if not save_path:
            return

        with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Month", "Profit", "Avg Return", "Count"])

            for i in range(12):
                w.writerow([
                    i + 1,
                    self.table.item(i, 1).text(),
                    self.table.item(i, 2).text(),
                    self.table.item(i, 3).text(),
                ])

        print("[CSV 저장 완료]")

    # -------------------------------------------------------
    # PDF 생성 (Windows 한글 경로 문제 해결판)
    # -------------------------------------------------------
    def save_pdf(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "PDF 저장", "", "PDF (*.pdf)")
        if not save_path:
            return

        font_path = get_korean_font_path()
        if not font_path:
            QMessageBox.warning(self, "오류", "한글 폰트를 찾을 수 없습니다.")
            return

        # 이미지 저장을 OS 임시폴더로 (Windows 한글 경로 문제 해결)
        profit_img = str(self.temp_dir / "profit_graph.png")
        rate_img = str(self.temp_dir / "rate_graph.png")

        months = list(range(1, 13))

        # 수익 그래프
        plt.figure(figsize=(10, 5))
        plt.bar(months, self.current_profit, color="#5DADE2")
        plt.title("월별 총 수익")
        plt.xlabel("월")
        plt.ylabel("수익 (원)")
        plt.grid(axis='y', linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(profit_img, dpi=200)
        plt.close()

        # 수익률 그래프
        plt.figure(figsize=(10, 5))
        plt.bar(months, self.current_rate, color="#48C9B0")
        plt.title("월별 평균 수익률 (%)")
        plt.xlabel("월")
        plt.ylabel("수익률 (%)")
        plt.grid(axis='y', linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(rate_img, dpi=200)
        plt.close()

        # PDF 생성
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font("KR", "", font_path, uni=True)
        pdf.set_font("KR", size=14)

        pdf.cell(0, 10, txt=f"{self.year_box.currentText()}년 월별 수익 분석", ln=True, align="C")
        pdf.ln(5)

        # 표 헤더
        pdf.set_font("KR", size=11)
        pdf.cell(20, 8, "월", 1)
        pdf.cell(40, 8, "총 수익", 1)
        pdf.cell(40, 8, "평균 수익률", 1)
        pdf.cell(30, 8, "종목 수", 1)
        pdf.ln()

        # 표 내용
        for i in range(12):
            pdf.set_font("KR", size=10)
            pdf.cell(20, 8, f"{i+1}월", 1)
            pdf.cell(40, 8, self.table.item(i, 1).text(), 1)
            pdf.cell(40, 8, self.table.item(i, 2).text(), 1)
            pdf.cell(30, 8, self.table.item(i, 3).text(), 1)
            pdf.ln()

        # 이미지 삽입 (임시폴더라 경로 안전)
        pdf.add_page()
        pdf.image(profit_img, x=15, w=180)

        pdf.add_page()
        pdf.image(rate_img, x=15, w=180)

        # 청약 리스트
        pdf.add_page()
        pdf.set_font("KR", size=14)
        pdf.cell(0, 10, txt="월별 청약 종목 리스트", ln=True)

        pdf.set_font("KR", size=10)

        for month in range(12):
            pdf.ln(3)
            pdf.cell(0, 8, f"{month+1}월", ln=True)

            if not self.monthly_items[month]:
                pdf.cell(0, 6, "- 없음", ln=True)
            else:
                for name in self.monthly_items[month]:
                    pdf.cell(0, 6, f"- {name}", ln=True)

        pdf.output(save_path)
        print("[PDF 저장 완료 →]", save_path)