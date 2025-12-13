# QTimer를 이용해 매일 오전 9시에 공모주 일정을 자동으로 확인하고
# 디스코드 알림을 보내는 스케줄러

from PyQt6.QtCore import QObject, QTimer
from datetime import datetime, date

from services.subscribe_service import load_subscribe_list
from services.completed_service import load_completed
from services.alarm import Alarm


class AlarmScheduler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.timer = QTimer(self)
        self.timer.setInterval(60 * 1000)  # 1분마다 체크
        self.timer.timeout.connect(self._check_and_notify)

        self.last_run_date = None

    def start(self):
        self.timer.start()
        self._check_and_notify()

    # 오전 9시 자동 알람
    def _check_and_notify(self, force: bool = False):
        now = datetime.now()
        today = now.date()

        if not force:
            if self.last_run_date == today:
                return
            if now.hour != 9:
                return

        self.last_run_date = today


        # 청약 시작 알람
        subscribe_list = load_subscribe_list()
        for item in subscribe_list:
            start_str = item.get("청약시작")
            if not start_str:
                continue

            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            except:
                continue

            if start_date == today:
                Alarm.alert_subscribe_start(
                    name=item.get("종목명", ""),
                    start_date=start_str,
                    broker=item.get("주관사", "")
                )

        # 상장 알람
        completed_list = load_completed()
        for item in completed_list:
            listing_str = item.get("상장일", "")
            if not listing_str:
                continue

            try:
                listing_date = datetime.strptime(listing_str, "%Y.%m.%d").date()
            except:
                continue

            if listing_date == today:
                Alarm.alert_listing(
                    name=item.get("종목명", ""),
                    listing_date=listing_str
                )

    # 디버그용: 청약일이 가장 가까운 종목을 찾아 알람 보내기
    def debug_subscribe_alarm(self):
        subscribe_list = load_subscribe_list()
        if not subscribe_list:
            return False

        today = date.today()
        candidates = []

        # today 와 가장 가까운 날짜 찾기
        for item in subscribe_list:
            start_str = item.get("청약시작")
            if not start_str:
                continue
            try:
                d = datetime.strptime(start_str, "%Y-%m-%d").date()
            except:
                continue

            diff = abs((d - today).days)
            candidates.append((diff, d))

        if not candidates:
            return False

        # 최소 차이 날짜 선택
        _, target_date = min(candidates, key=lambda x: x[0])

        found = False
        for item in subscribe_list:
            if item.get("청약시작") == target_date.strftime("%Y-%m-%d"):
                Alarm.alert_subscribe_start(
                    name=item.get("종목명", ""),
                    start_date=item.get("청약시작"),
                    broker=item.get("주관사", "")
                )
                found = True

        return found


    # 디버그용: 상장일이 가장 가까운 종목을 찾아 알람 보내기
    def debug_listing_alarm(self):
        completed_list = load_completed()
        if not completed_list:
            return False

        today = date.today()
        candidates = []

        for item in completed_list:
            listing_str = item.get("상장일")
            if not listing_str:
                continue

            try:
                d = datetime.strptime(listing_str, "%Y.%m.%d").date()
            except:
                continue

            diff = abs((d - today).days)
            candidates.append((diff, d))

        if not candidates:
            return False

        # 가장 가까운 상장일
        _, target_date = min(candidates, key=lambda x: x[0])

        found = False
        for item in completed_list:
            try:
                d = datetime.strptime(item["상장일"], "%Y.%m.%d").date()
            except:
                continue

            if d == target_date:
                Alarm.alert_listing(
                    name=item.get("종목명", ""),
                    listing_date=item.get("상장일")
                )
                found = True

        return found