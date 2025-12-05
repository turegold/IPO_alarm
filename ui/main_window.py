# main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.schedule_tab import ScheduleTab
from ui.result_tab import ResultTab
from ui.analysis_tab import AnalysisTab
from ui.settings_tab import SettingsTab
from ui.subscribe_tab import SubscribeTab
from services.alarm_scheduler import AlarmScheduler   # ★ 추가

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("공모주 일정·수익 분석 자동화 시스템")
        self.resize(900, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 🔔 알람 스케줄러 생성 + 시작
        self.alarm_scheduler = AlarmScheduler(self)
        self.alarm_scheduler.start()

        # 탭 구성
        self.schedule_tab = ScheduleTab()
        self.subscribe_tab = SubscribeTab()
        self.result_tab = ResultTab()
        self.analysis_tab = AnalysisTab()
        self.settings_tab = SettingsTab(main_window=self)   # ★ self 넘겨주기

        self.tabs.addTab(self.schedule_tab, "공모주 일정")
        self.tabs.addTab(self.subscribe_tab, "청약 예정")
        self.tabs.addTab(self.result_tab, "청약 완료 / 수익 입력")
        self.tabs.addTab(self.analysis_tab, "월별 수익 분석")
        self.tabs.addTab(self.settings_tab, "알림 / 설정")

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        tab_name = self.tabs.tabText(index)

        if tab_name == "청약 완료 / 수익 입력":
            self.result_tab.refresh()

        if tab_name == "청약 예정":
            if hasattr(self.subscribe_tab, "refresh"):
                self.subscribe_tab.refresh()