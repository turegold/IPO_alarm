# services/subscribe_service.py

from pathlib import Path
import json
from datetime import datetime

from services.date_utils import parse_schedule, is_expired


SUBSCRIBE_PATH = Path("data") / "subscribe.json"
COMPLETED_PATH = Path("data") / "completed.json"


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def _save_json(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 1) 기본 로더들
# ============================================================

def load_subscribe_list():
    """기본 subscribe.json만 읽기 (정리 없음)"""
    return _read_json(SUBSCRIBE_PATH, [])


def load_completed_names():
    """completed.json에서 종목명만 set으로 반환"""
    data = _read_json(COMPLETED_PATH, [])
    return {d.get("종목명") for d in data}


# ============================================================
# 2) 청약 예정 등록
# ============================================================

def register_subscribe(item: dict, year: int):
    """
    청약 예정 등록 로직
    UI에서 메시지만 띄우고 실제 등록 처리는 여기서 한다.
    return: (success: bool, message: str)
    """

    # 이미 청약 완료된 종목은 등록 불가
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
        "알림": True,  # 기본 ON
    }

    subscribe_list.append(new_entry)
    _save_json(SUBSCRIBE_PATH, subscribe_list)

    return True, f"{item['종목명']} 청약 예정에 등록되었습니다."


# ============================================================
# 3) 자동 정리 (지난 종목 / 완료된 종목 제거)
# ============================================================

def load_subscribe_with_cleanup():
    """
    - subscribe.json 로드
    - 완료된 종목 제거
    - 청약 종료일 지난 종목 제거
    - 알림 필드 없으면 기본 True 추가
    - 정리 결과 저장 후 목록 반환
    """

    subscribe_list = load_subscribe_list()
    completed_names = load_completed_names()
    today = datetime.now().date()

    cleaned = []

    for item in subscribe_list:
        name = item.get("종목명")

        # 1) 청약 완료된 종목 자동 제거
        if name in completed_names:
            continue

        # 2) 청약 종료일이 지났으면 제거
        try:
            end = item.get("청약종료", "")
            if end:
                end_date = datetime.strptime(end, "%Y-%m-%d").date()
                if today > end_date:
                    continue
        except:
            pass

        # 3) 알림 필드가 없으면 기본값 True
        if "알림" not in item:
            item["알림"] = True

        cleaned.append(item)

    # 변경분 저장
    _save_json(SUBSCRIBE_PATH, cleaned)

    return cleaned


# ============================================================
# 4) 메모 업데이트
# ============================================================

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


# ============================================================
# 5) 알림 설정 (ON/OFF)
# ============================================================

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


# ============================================================
# 6) 종목 삭제
# ============================================================

def delete_item(name: str):
    items = load_subscribe_list()
    filtered = [it for it in items if it.get("종목명") != name]
    _save_json(SUBSCRIBE_PATH, filtered)


# ============================================================
# 7) 전체 저장 (필요시)
# ============================================================

def save_subscribe_list(items):
    _save_json(SUBSCRIBE_PATH, items)