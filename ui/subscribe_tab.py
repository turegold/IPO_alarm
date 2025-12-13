# 청약 예정으로 등록된 공모주를 조회,정리하고, 메모 작성,알림 ON/OFF,선택 삭제를 관리하는 청약 예정 관리 UI 탭

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt

from services.subscribe_service import (
    load_subscribe_with_cleanup,
    update_memo,
    delete_item,
    set_alarm_enabled,
)

# 청약 예정 종목 관리 UI
class SubscribeTab(QWidget):

    def __init__(self):
        super().__init__()
        self.block_signal = False  # 셀 변경 시 무한 호출 방지
        self.init_ui()


    # UI 구성
    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("청약 예정 종목 관리")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            "공모주 일정에서 '청약 예정'으로 등록한 종목들을 관리합니다.\n"
            "- 청약 종료일이 지난 종목은 자동 삭제됩니다.\n"
            "- 청약 완료된 종목도 자동 제거됩니다.\n"
            "- 메모는 셀 수정 시 자동 저장됩니다.\n"
            "- 알림은 기본 ON 상태이며, 버튼으로 ON/OFF를 설정할 수 있습니다."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: gray;")
        layout.addWidget(desc)

        # 버튼 영역
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton("새로고침")
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("선택 삭제")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 테이블
        self.table = QTableWidget()
        # 0: 종목명, 1: 청약 시작, 2: 청약 종료, 3: 증권사, 4: 메모, 5: 상태, 6: 알림 설정
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["종목명", "청약 시작일", "청약 종료일", "증권사", "메모", "상태", "알림"]
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # 메모 수정 시 JSON 저장
        self.table.cellChanged.connect(self.on_cell_changed)

        layout.addWidget(self.table)
        self.setLayout(layout)

        # 첫 로딩
        self.refresh()


    # 서비스 레이어에서 청약 예정 목록을 불러오는 함수
    # 자동 정리된 최신 상태로 테이블을 갱신
    def refresh(self):
        self.block_signal = True

        items = load_subscribe_with_cleanup()
        self.update_table(items)

        self.block_signal = False

    # 로드된 데이터를 테이블에 표시하고, 각 행에 알림 ON/OFF 토글 버튼을 생성하는 함수
    def update_table(self, items):
        self.table.setRowCount(0)

        for item in items:
            row = self.table.rowCount()
            self.table.insertRow(row)

            name = item.get("종목명", "")
            start = item.get("청약시작", "")
            end = item.get("청약종료", "")
            broker = item.get("주관사", "")
            memo = item.get("메모", "")
            status = item.get("상태", "")
            alarm_enabled = item.get("알림", True)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(start))
            self.table.setItem(row, 2, QTableWidgetItem(end))
            self.table.setItem(row, 3, QTableWidgetItem(broker))
            self.table.setItem(row, 4, QTableWidgetItem(memo))
            self.table.setItem(row, 5, QTableWidgetItem(status))

            # 알림 설정 버튼
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setChecked(alarm_enabled)
            btn.setText("ON" if alarm_enabled else "OFF")

            # late-binding 방지용 클로저
            btn.clicked.connect(self._make_alarm_handler(name, btn))

            self.table.setCellWidget(row, 6, btn)

    # 버튼 클릭 시 알림 상태를 서비스에 저장, 버튼 텍스트를 갱신하는 함수
    def _make_alarm_handler(self, name: str, button: QPushButton):
        def handler(checked: bool):
            # 서비스에 저장
            set_alarm_enabled(name, checked)
            # 버튼 텍스트 갱신
            button.setText("ON" if checked else "OFF")
        return handler

    # 메모 컬럼 수정 시 해당 종목의 메모를 자동 저장하는 함수
    def on_cell_changed(self, row, col):
        if self.block_signal:
            return
        if col != 4:  # 메모 컬럼만 저장
            return

        name_item = self.table.item(row, 0)
        memo_item = self.table.item(row, 4)

        if not name_item or not memo_item:
            return

        name = name_item.text()
        memo = memo_item.text()

        update_memo(name, memo)

    # 선택한 청약 예정 종목을 삭제하는 함수
    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "삭제 실패", "삭제할 항목을 선택하세요.")
            return

        name_item = self.table.item(row, 0)
        if not name_item:
            return

        name = name_item.text()

        delete_item(name)
        QMessageBox.information(self, "삭제 완료", f"{name} 종목이 삭제되었습니다.")

        self.refresh()