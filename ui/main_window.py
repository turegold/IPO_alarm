from PyQt6.QtWidgets import QMainWindow, QTabWidget
from ui.schedule_tab import ScheduleTab
from ui.result_tab import ResultTab
from ui.analysis_tab import AnalysisTab
from ui.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("공모주 일정·수익 분석 자동화 시스템")
        self.resize(900, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 탭 구성
        self.schedule_tab = ScheduleTab()
        self.result_tab = ResultTab()
        self.analysis_tab = AnalysisTab()
        self.settings_tab = SettingsTab()

        # 탭 추가
        self.tabs.addTab(self.schedule_tab, "공모주 일정")
        self.tabs.addTab(self.result_tab, "청약 완료 / 수익 입력")
        self.tabs.addTab(self.analysis_tab, "월별 수익 분석")
        self.tabs.addTab(self.settings_tab, "설정")