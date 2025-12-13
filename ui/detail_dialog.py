# 공모주 상세 크롤링 결과를 기반으로 회사 로고, 업종, 공모가격, 공모주식 수, 증권사 배정 정보를 표 형태로 보여주는 PyQt 상세 정보 다이얼로그 UI

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHeaderView

import requests

# 단일 공모주의 상세 정보를 시각적으로 보여주는 팝업 다이얼로그
class DetailDialog(QDialog):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data  # crawl_detail() 결과 + 기본 종목 정보
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"{self.data.get('종목명', '')} - 상세 보기")
        self.resize(820, 620)

        main_layout = QVBoxLayout(self)

        # 상단 헤더(회사 로고 이미지, 종목명, 업종)
        header_layout = QHBoxLayout()

        # 로고
        logo_label = QLabel()
        logo_label.setFixedSize(100, 60)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFrameShape(QFrame.Shape.NoFrame)

        logo_url = self.data.get("logo")

        if logo_url:
            try:
                res = requests.get(logo_url, timeout=5)
                pixmap = QPixmap()
                pixmap.loadFromData(res.content)

                if pixmap.isNull():
                    logo_label.setText("No Logo")
                else:
                    logo_label.setPixmap(pixmap.scaled(
                        100, 60,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))
            except Exception:
                logo_label.setText("No Logo")
        else:
            logo_label.setText("No Logo")

        header_layout.addWidget(logo_label)

        # 회사명, 업종
        text_layout = QVBoxLayout()

        name_label = QLabel(self.data.get("종목명", "종목명 없음"))
        name_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        text_layout.addWidget(name_label)

        sector = self.data.get("업종", "")
        sector_label = QLabel(sector)
        sector_label.setStyleSheet("color: gray; font-size: 13px;")
        text_layout.addWidget(sector_label)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # 구분선
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line1)

        # 공모 가격 테이블
        price_title = QLabel("공모 가격 정보")
        price_title.setStyleSheet("font-weight: bold; margin-top: 6px; font-size: 15px;")
        main_layout.addWidget(price_title)

        price_dict = self.data.get("공모가격", {})

        ordered_keys = [
            "(희망)공모가격",
            "(희망)공모금액",
            "(확정)공모가격",
            "(확정)공모금액",
            "수요예측일",
            "공모청약일",
            "납일일",
            "환불일",
            "상장일",
            "청약증거금율",
            "청약경쟁률",
        ]

        rows = [(k, price_dict[k]) for k in ordered_keys if k in price_dict]

        price_table = self._create_kv_table(rows, ["항목", "내용"])
        main_layout.addWidget(price_table)

        # 구분선
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line2)


        # 공모 주식 수 및 배정 테이블
        share_title = QLabel("공모 주식 수 및 배정")
        share_title.setStyleSheet("font-weight: bold; margin-top: 6px; font-size: 15px;")
        main_layout.addWidget(share_title)

        share_rows = self.data.get("공모주식수", [])
        if share_rows:
            share_table = self._create_matrix_table(share_rows)
            main_layout.addWidget(share_table)
        else:
            main_layout.addWidget(QLabel("공모 주식 수 정보 없음"))

        # 구분선
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line3)


        # 증권사 배정 테이블
        broker_title = QLabel("증권사 및 배정 수량")
        broker_title.setStyleSheet("font-weight: bold; margin-top: 6px; font-size: 15px;")
        main_layout.addWidget(broker_title)

        broker_rows = self.data.get("증권사배정", [])
        if broker_rows:
            broker_table = self._create_matrix_table(broker_rows)
            main_layout.addWidget(broker_table)
        else:
            main_layout.addWidget(QLabel("증권사 배정 정보 없음"))


    # Key-Value 테이블 생성
    def _create_kv_table(self, rows, headers):
        table = QTableWidget()
        table.setColumnCount(2)
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(headers)

        for r, (k, v) in enumerate(rows):
            table.setItem(r, 0, QTableWidgetItem(str(k)))
            table.setItem(r, 1, QTableWidgetItem(str(v)))

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        return table


    # 2D 테이블 생성
    def _create_matrix_table(self, rows):
        col_count = max(len(r) for r in rows)
        table = QTableWidget()
        table.setColumnCount(col_count)
        table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(str(val)))

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        return table