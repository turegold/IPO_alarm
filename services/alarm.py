# services/alarm.py

import requests
from datetime import datetime
from services.settings_service import load_webhook_url


class Alarm:
    """
    디스코드 알림 기능을 담당하는 통합 클래스.
    어디서든 Alarm.send("메시지") 로 호출하면 됨.
    """

    @staticmethod
    def send(message: str):
        """
        디스코드 웹훅으로 메시지를 보낸다.
        설정 탭에서 저장된 webhook URL을 자동으로 불러옴.
        """
        webhook_url = load_webhook_url()

        if not webhook_url:
            return False, "⚠ 웹훅 URL이 설정되어 있지 않습니다."

        payload = {
            "content": message
        }

        try:
            resp = requests.post(webhook_url, json=payload, timeout=5)

            if resp.status_code == 204:
                return True, "전송 성공"
            else:
                return False, f"전송 실패 (HTTP {resp.status_code})"

        except Exception as e:
            return False, f"에러 발생: {e}"

    # -------------------------------------------------
    # 확장: 시스템 자체에 필요한 메시지 포맷 함수들
    # -------------------------------------------------

    @staticmethod
    def alert_subscribe_start(name, start_date, broker):
        """청약 시작 알림 메시지"""
        msg = (
            f"📢 **{name}** 공모주 청약이 오늘 시작됩니다!\n"
            f"- 시작일: {start_date}\n"
            f"- 증권사: {broker}"
        )
        return Alarm.send(msg)

    @staticmethod
    def alert_subscribe_end(name, end_date):
        """청약 종료 알림 메시지"""
        msg = (
            f"⏰ **{name}** 공모주 청약이 오늘 마감됩니다!\n"
            f"- 종료일: {end_date}\n"
            f"서두르세요!"
        )
        return Alarm.send(msg)

    @staticmethod
    def alert_listing(name, listing_date):
        """상장일 알림 메시지"""
        msg = (
            f"🎉 **{name}** 오늘 상장합니다!\n"
            f"- 상장일: {listing_date}\n"
            f"수익 입력을 잊지 마세요!"
        )
        return Alarm.send(msg)