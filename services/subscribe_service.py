# 청약 예정 목록을 등록,정리,수정,삭제하고 날짜 기준으로 자동정리를 수행하는 관리 서비스 코드

from pathlib import Path
import json
from datetime import datetime

from services.date_utils import parse_schedule, is_expired


SUBSCRIBE_PATH = Path("data") / "subscribe.json"
COMPLETED_PATH = Path("data") / "completed.json"

# JSON 파일을 안정하게 읽기 위한 함수
def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

# JSON 파일로 저장하는 함수
def _save_json(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



# subscribe.json을 그대로 로드해서 반환하는 함수
def load_subscribe_list():
    return _read_json(SUBSCRIBE_PATH, [])

# completed.json에서 청약 완료된 종목명만 set으로 반환하는 함수
def load_completed_names():
    data = _read_json(COMPLETED_PATH, [])
    return {d.get("종목명") for d in data}



# 공모주를 청약 예정 목록에 등록하는 함수
def register_subscribe(item: dict, year: int):

    # 이미 청약 완료된 종목은 등록 불가 처리
    completed_names = load_completed_names()
    if item["종목명"] in completed_names:
        return False, "이미 청약 완료한 공모주입니다."

    # 이미 subscribe에 존재하는지 확인
    subscribe_list = load_subscribe_list()
    for s in subscribe_list:
        if s.get("종목명") == item["종목명"]:
            return False, "이미 청약 예정에 등록된 종목입니다."

    # 날짜 파싱
    start, end = parse_schedule(item["공모일정"], year)
    if is_expired(start, end):
        return False, "이미 지난 공모주입니다."

    # 저장 객체 생성
    new_entry = {
        "종목명": item["종목명"],
        "청약시작": start.strftime("%Y-%m-%d") if start else "",
        "청약종료": end.strftime("%Y-%m-%d") if end else "",
        "상장일": f"{year}.{item['상장일']}",
        "주관사": item.get("주간사", ""),
        "메모": "",
        "상태": "대기",
        "알림": True,
    }

    subscribe_list.append(new_entry)
    _save_json(SUBSCRIBE_PATH, subscribe_list)

    return True, f"{item['종목명']} 청약 예정에 등록되었습니다."



# subscribe 목록을 불러와 유효하지 않은 공모주를 제거하는 함수
def load_subscribe_with_cleanup():

    subscribe_list = load_subscribe_list()
    completed_names = load_completed_names()
    today = datetime.now().date()

    cleaned = []

    for item in subscribe_list:
        name = item.get("종목명")

        # 청약 완료된 종목 자동 제거
        if name in completed_names:
            continue

        # 청약 종료일이 지났으면 제거
        try:
            end = item.get("청약종료", "")
            if end:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
                if today > end_date:
                    continue
        except:
            pass

        # 알림 필드가 없으면 기본값 True
        if "알림" not in item:
            item["알림"] = True

        cleaned.append(item)

    # 변경분 저장
    _save_json(SUBSCRIBE_PATH, cleaned)

    return cleaned



# 특정 종목의 메모 내용을 수정하는 함수
def update_memo(name: str, memo: str):
    items = load_subscribe_list()

    changed = False
    for it in items:
        if it.get("종목명") == name:
            it["메모"] = memo
            changed = True
            break

    if changed:
        _save_json(SUBSCRIBE_PATH, items)



# 특정 종목의 알림 활설화 여부를 설정하는 함수
def set_alarm_enabled(name: str, enabled: bool):
    items = load_subscribe_list()

    changed = False
    for it in items:
        if it.get("종목명") == name:
            it["알림"] = bool(enabled)
            changed = True
            break

    if changed:
        _save_json(SUBSCRIBE_PATH, items)



# 청약 예정 목록에서 특정 종목을 제거하는 함수
def delete_item(name: str):
    items = load_subscribe_list()
    filtered = [it for it in items if it.get("종목명") != name]
    _save_json(SUBSCRIBE_PATH, filtered)



# 외부에서 가공한 subscribe 목록을 저장하는 함수
def save_subscribe_list(items):
    _save_json(SUBSCRIBE_PATH, items)