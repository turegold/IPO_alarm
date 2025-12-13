# 공모주 일정 문자열을 시작일, 종료일로 파싱하고,
# 해당 공모주가 이미 종료되었는지 판단하는 날짜 유틸리티

from datetime import datetime

# 문자열을 파싱하여 시작일,종료일로 변환하는 함수
def parse_schedule(schedule: str, year: int):
    try:
        s, e = schedule.split("~")
        s = s.strip().replace(".", "-")
        e = e.strip().replace(".", "-")

        start = datetime.strptime(f"{year}-{s}", "%Y-%m-%d")
        end = datetime.strptime(f"{year}-{e}", "%Y-%m-%d")
        return start, end
    except:
        return None, None


# 이미 지난 공모주인지 판단하는 함수
def is_expired(start, end):
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