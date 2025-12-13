# 저장된 공모주 관련 JSON 파일들을 읽어 공모주 목록과
# '청약 관리 / 청약 예정' 종목명을 조회하는 유틸리티

from pathlib import Path
import json

DATA_DIR = Path("data")

# 해당 월의 공모주 전체 목록을 리스트로 반환
def load_ipo_list(year: int, month: int):
    path = DATA_DIR / f"ipo_{year}_{month:02d}.json"
    if not path.exists():
        return []
    try:
        return json.load(path.open("r", encoding="utf-8"))
    except:
        return []

# 청약 완료된 종목명만 set 형태로 반환하는 함수
def load_completed_names():
    path = DATA_DIR / "completed.json"
    if not path.exists():
        return set()
    try:
        data = json.load(path.open("r", encoding="utf-8"))
        return {d.get("종목명") for d in data}
    except:
        return set()

# subsribe.json을 읽어 청약 예정 종목명만 set 형태로 반환하는 함수
def load_subscribe_names():
    path = DATA_DIR / "subscribe.json"
    if not path.exists():
        return set()
    try:
        data = json.load(path.open("r", encoding="utf-8"))
        return {d.get("종목명") for d in data}
    except:
        return set()