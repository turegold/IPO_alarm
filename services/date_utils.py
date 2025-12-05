# services/date_utils.py

from datetime import datetime


def parse_schedule(schedule: str, year: int):
    """
    schedule: "12.10 ~ 12.11"
    return: (datetime 시작, datetime 종료)
    """
    try:
        s, e = schedule.split("~")
        s = s.strip().replace(".", "-")
        e = e.strip().replace(".", "-")

        start = datetime.strptime(f"{year}-{s}", "%Y-%m-%d")
        end = datetime.strptime(f"{year}-{e}", "%Y-%m-%d")
        return start, end
    except:
        return None, None


def is_expired(start, end):
    """
    이미 지난 공모주인지 판단
    """
    if not start or not end:
        return False

    now = datetime.now()

    # 종료일 이후
    if now.date() > end.date():
        return True

    # 종료일 당일 16시 이후
    if now.date() == end.date() and now.hour >= 16:
        return True

    return False