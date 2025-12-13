# 공모주 청약이 완료된 종목을 completed.json에 저장 및 관리하고,
# 확정 공모가를 크롤링해 자동 반영하며 기존 청약 목록에서 제거하는 로직

from pathlib import Path
import json
from services.detail_crawler import crawl_detail


COMPLETED_PATH = Path("data") / "completed.json"
SUBSCRIBE_PATH = Path("data") / "subscribe.json"

# completed.json 파일을 읽어 청약 완료 종목을 불러오는 함수
def load_completed():
    if not COMPLETED_PATH.exists():
        return []
    try:
        return json.load(COMPLETED_PATH.open("r", encoding="utf-8"))
    except:
        return []


# 전달받은 데이터를 completed.json 파일에 저장하는 함수
def save_completed(data):
    json.dump(data, COMPLETED_PATH.open("w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


# 특정 종목을 청약 완료 상태로 등록하는 함수
def mark_completed(item: dict, year: int):
    completed = load_completed()

    # 이미 존재하는가?
    for c in completed:
        if c.get("종목명") == item["종목명"]:
            return False, "이미 청약 완료로 등록된 종목입니다."

    # 상세 페이지에서 확정 공모가
    확정공모가 = None
    if item.get("상세URL"):
        try:
            detail = crawl_detail(item["상세URL"])
            price_info = detail.get("공모가격", {})
            if "(확정)공모가격" in price_info:
                price_str = price_info["(확정)공모가격"]
                확정공모가 = int(
                    price_str.replace("원", "").replace(",", "").strip()
                )
        except:
            pass

    raw_listing = item.get("상장일", "")
    fixed_listing = f"{year}.{raw_listing}" if raw_listing else ""

    new_entry = {
        "종목명": item["종목명"],
        "상장일": fixed_listing,
        "배정수량": "",
        "매수가": 확정공모가 if 확정공모가 else "",
        "매도가": "",
        "상세URL": item.get("상세URL", ""),
    }

    completed.append(new_entry)
    save_completed(completed)

    # 청약 예정 목록에서 삭제
    if SUBSCRIBE_PATH.exists():
        try:
            subscribe_list = json.load(SUBSCRIBE_PATH.open("r", encoding="utf-8"))
        except:
            subscribe_list = []
        new_list = [s for s in subscribe_list if s.get("종목명") != item["종목명"]]
        json.dump(new_list, SUBSCRIBE_PATH.open("w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)

    return True, f"{item['종목명']} 청약 완료 목록에 저장되었습니다."