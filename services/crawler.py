# services/crawler.py
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.ipostock.co.kr"


def get_ipo_list(year: int, month: int):
    url = f"{BASE_URL}/sub03/ipo04.asp?str1={year}&str2={month}"
    res = requests.get(url)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find(
        "table",
        attrs={"style": "border-collapse:collapse; margin:0px 0px 0px 0px;"},
    )
    rows = table.find_all("tr", height="30")

    ipo_data = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 10:
            continue

        # 공모일정 (NBSP → 공백 치환)
        schedule = cells[1].get_text(strip=True).replace("\xa0", " ")

        # 목록에서 보이는 이름 & 상세페이지 링크
        item_tag = cells[2].find("a")
        short_name = item_tag.get_text(strip=True) if item_tag else ""
        href = item_tag["href"] if item_tag and item_tag.has_attr("href") else None

        full_name = short_name
        detail_url = None

        # 상세페이지에서 실제 전체 종목명 가져오기
        if href:
            if href.startswith("http"):
                detail_url = href
            else:
                detail_url = BASE_URL + href.lstrip(".")

            try:
                detail_res = requests.get(detail_url)
                detail_res.encoding = "utf-8"
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                full_name_tag = detail_soup.select_one("strong.view_tit")
                if full_name_tag:
                    full_name = full_name_tag.get_text(strip=True)
            except Exception as e:
                print("상세 페이지 에러:", e)

        hope_price = cells[3].get_text(strip=True)
        final_price = cells[4].get_text(strip=True)
        money = cells[5].get_text(strip=True)
        refund_date = cells[6].get_text(strip=True)
        listing_date = cells[7].get_text(strip=True)
        rate = cells[8].get_text(strip=True)
        broker = cells[9].get_text(strip=True)

        ipo_data.append(
            {
                "종목명": full_name,
                "공모일정": schedule,
                "희망공모가": hope_price,
                "공모가": final_price,
                "공모금액": money,
                "환불일": refund_date,
                "상장일": listing_date,
                "경쟁률": rate,
                "주간사": broker,
                "상세URL": detail_url,   # ⭐ 여기 추가
            }
        )

    return ipo_data


def save_ipo_json(year: int, month: int):
    data = get_ipo_list(year, month)

    base_dir = Path(__file__).resolve().parent
    project_root = base_dir.parent

    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = data_dir / f"ipo_{year}_{month:02d}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {file_path} 에 {len(data)}개 종목 저장 완료 (덮어쓰기).")


if __name__ == "__main__":
    save_ipo_json(2025, 12)