# 설정 탭에서 디스코드 웹훅 URL을 저장/테스트하고, 알람 스케줄러의 청약,상장 알림을 디버그로 강제 실행할 수 있게 해주는 PyQt UI탭

from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from services.settings_service import load_webhook_url, save_webhook_url
from services.alarm import Alarm


# 설정 탭을 구성하는 UI
class SettingsTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    # UI 초기화
    def init_ui(self):
        root = QVBoxLayout()

        # 웹훅 URL 입력
        form = QFormLayout()

        self.webhook_input = QLineEdit()
        self.webhook_input.setText(load_webhook_url())
        form.addRow("디스코드 웹훅 URL:", self.webhook_input)

        root.addLayout(form)

        # 버튼 공통 스타일
        def make_big_button(text):
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setMinimumHeight(32)
            return btn

        # 버튼들
        save_btn = make_big_button("웹훅 URL 저장")
        save_btn.clicked.connect(self.save_webhook)
        root.addWidget(save_btn)

        test_btn = make_big_button("웹훅 테스트 메시지 보내기")
        test_btn.clicked.connect(self.send_test_message)
        root.addWidget(test_btn)

        debug_sub_btn = make_big_button("청약 시작 알람 디버그 실행")
        debug_sub_btn.clicked.connect(self.debug_subscribe_alarm)
        root.addWidget(debug_sub_btn)

        debug_list_btn = make_big_button("상장 알람 디버그 실행")
        debug_list_btn.clicked.connect(self.debug_listing_alarm)
        root.addWidget(debug_list_btn)

        root.addStretch()
        self.setLayout(root)


    # 웹훅 URL을 settings.json에 저장하고 완료 메시지를 띄우는 함수
    def save_webhook(self):
        url = self.webhook_input.text().strip()
        save_webhook_url(url)
        QMessageBox.information(self, "저장 완료", "웹훅 URL이 저장되었습니다.")


    # Alarm.send()로 테스트 메시지를 디스코드에 보내고 성공/실패를 알림창으로 보여주는 함수
    def send_test_message(self):
        ok, msg = Alarm.send("🔔 테스트 메시지: 웹훅이 정상적으로 동작합니다.")
        if ok:
            QMessageBox.information(self, "전송 성공", msg)
        else:
            QMessageBox.warning(self, "전송 실패", msg)

    # 가장 가까운 청약 시작 알림을 강제로 발송하는 함수
    def debug_subscribe_alarm(self):
        if not self.main_window or not hasattr(self.main_window, "alarm_scheduler"):
            QMessageBox.warning(self, "실행 실패", "알람 스케줄러가 초기화되지 않았습니다.")
            return

        scheduler = self.main_window.alarm_scheduler
        found = scheduler.debug_subscribe_alarm()

        if not found:
            QMessageBox.warning(self, "알림 없음", "디버그할 청약 예정 종목이 없습니다.")
        else:
            QMessageBox.information(self, "실행 완료", "청약 시작 알람 디버그 실행 완료!")

    # 가장 가까운 상장 알림을 강제로 발송하는 함수
    def debug_listing_alarm(self):
        if not self.main_window or not hasattr(self.main_window, "alarm_scheduler"):
            QMessageBox.warning(self, "실행 실패", "알람 스케줄러가 초기화되지 않았습니다.")
            return

        scheduler = self.main_window.alarm_scheduler
        found = scheduler.debug_listing_alarm()

        if not found:
            QMessageBox.warning(self, "알림 없음", "디버그할 상장 종목이 없습니다.")
        else:
            QMessageBox.information(self, "실행 완료", "상장 알람 디버그 실행 완료!")