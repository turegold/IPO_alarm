# 공모주 투자 결과를 CSV와 PDF로 저장하고, 월별 수익, 수익률 그래프를 생성해 리포트 형태로 출력하는 파일 저장/리포트 생성 모듈


from pathlib import Path
import csv
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from fpdf import FPDF
import tempfile
import os
os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.warning=false"



# 폰트 경로 설정
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
FONT_PATH = DATA_DIR / "fonts" / "Noto_Sans_KR" / "NotoSansKR-VariableFont_wght.ttf"

TEMP_DIR = Path(tempfile.gettempdir())



# Matplotlib 한글 폰트 설정
if FONT_PATH.exists():
    font_manager.fontManager.addfont(str(FONT_PATH))
    rc("font", family="Noto Sans KR")

# 월별 요약 데이터를 CSV 파일로 저장하는 함수
def save_csv(path, table_widget):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Month", "Profit", "Avg Return", "Count"])

        for i in range(12):
            w.writerow([
                i + 1,
                table_widget.item(i, 1).text(),
                table_widget.item(i, 2).text(),
                table_widget.item(i, 3).text(),
            ])

# 월별 총 수익 / 평균 수익률 그래프를 matplotlib으로 생성하는 함수
def create_graphs(current_profit, current_rate):
    # 그래프를 임시폴더에 생성하고 경로를 반환
    profit_img = str(TEMP_DIR / "profit_graph.png")
    rate_img = str(TEMP_DIR / "rate_graph.png")

    months = list(range(1, 13))

    # 총 수익 그래프
    plt.figure(figsize=(10, 5))
    plt.bar(months, current_profit, color="#5DADE2")
    plt.title("월별 총 수익")
    plt.xlabel("월")
    plt.ylabel("수익 (원)")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(profit_img, dpi=200)
    plt.close()

    # 평균 수익률 그래프
    plt.figure(figsize=(10, 5))
    plt.bar(months, current_rate, color="#48C9B0")
    plt.title("월별 평균 수익률 (%)")
    plt.xlabel("월")
    plt.ylabel("수익률 (%)")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(rate_img, dpi=200)
    plt.close()

    return profit_img, rate_img

# 종합 투자 리포트 PDF를 생성하는 함수
def save_pdf(path, year, table_widget, monthly_items, current_profit, current_rate, monthly_qty):

    if not FONT_PATH.exists():
        raise FileNotFoundError("한글 폰트를 찾을 수 없습니다.")

    png_profit, png_rate = create_graphs(current_profit, current_rate)

    pdf = FPDF()
    pdf.add_page()

    pdf.add_font("KR", "", str(FONT_PATH), uni=True)
    pdf.set_font("KR", size=14)

    pdf.cell(0, 10, txt=f"{year}년 월별 수익 분석", ln=True, align="C")
    pdf.ln(5)

    # -------------------
    # 월별 요약 테이블
    # -------------------
    pdf.set_font("KR", size=11)
    pdf.cell(20, 8, "월", 1)
    pdf.cell(40, 8, "총 수익", 1)
    pdf.cell(40, 8, "평균 수익률", 1)
    pdf.cell(30, 8, "종목 수", 1)
    pdf.ln()

    for i in range(12):
        pdf.set_font("KR", size=10)
        pdf.cell(20, 8, f"{i+1}월", 1)
        pdf.cell(40, 8, table_widget.item(i, 1).text(), 1)
        pdf.cell(40, 8, table_widget.item(i, 2).text(), 1)
        pdf.cell(30, 8, table_widget.item(i, 3).text(), 1)
        pdf.ln()

    # -------------------
    # 그래프 페이지 2장
    # -------------------
    pdf.add_page()
    pdf.image(png_profit, x=15, w=180)

    pdf.add_page()
    pdf.image(png_rate, x=15, w=180)

    # -------------------
    # 월별 상세 페이지
    # -------------------
    col_widths = [45, 23, 23, 18, 35, 26]

    for month_idx in range(12):
        pdf.add_page()
        pdf.set_font("KR", size=14)
        pdf.cell(0, 10, txt=f"{year}년 {month_idx+1}월 청약 상세", ln=True)
        pdf.ln(4)

        items = monthly_items[month_idx]

        # 데이터 없음
        if not items:
            pdf.set_font("KR", size=11)
            pdf.cell(0, 10, "해당 월 청약 내역이 없습니다.", ln=True)
            continue

        # 헤더
        pdf.set_font("KR", size=10)
        headers = ["종목명", "매수가", "매도가", "수량", "수익", "수익률(%)"]
        for w, name in zip(col_widths, headers):
            pdf.cell(w, 8, name, 1, 0, "C")
        pdf.ln()

        # 행 데이터 추가
        for it in items:
            pdf.cell(col_widths[0], 8, it["name"], 1)
            pdf.cell(col_widths[1], 8, f"{it['buy']:,}", 1, 0, "R")
            pdf.cell(col_widths[2], 8, f"{it['sell']:,}", 1, 0, "R")
            pdf.cell(col_widths[3], 8, f"{it['qty']:,}", 1, 0, "R")
            pdf.cell(col_widths[4], 8, f"{it['profit']:,}", 1, 0, "R")
            pdf.cell(col_widths[5], 8, f"{it['rate']:.2f}", 1, 0, "R")
            pdf.ln()

        # 합계 행
        total_profit = current_profit[month_idx]
        total_qty = monthly_qty[month_idx]
        avg_rate = current_rate[month_idx]

        pdf.set_font("KR", size=10)
        pdf.cell(col_widths[0], 8, "합계", 1)
        pdf.cell(col_widths[1], 8, "", 1)
        pdf.cell(col_widths[2], 8, "", 1)
        pdf.cell(col_widths[3], 8, f"{total_qty:,}", 1, 0, "R")
        pdf.cell(col_widths[4], 8, f"{total_profit:,}", 1, 0, "R")
        pdf.cell(col_widths[5], 8, f"{avg_rate:.2f}", 1, 0, "R")

    pdf.output(path)