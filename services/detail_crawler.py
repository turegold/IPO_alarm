# services/detail_crawler.py

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.ipostock.co.kr"


def fetch_detail_page(url: str):
    res = requests.get(url)
    res.encoding = "utf-8"
    return BeautifulSoup(res.text, "html.parser")


# ---------------------------------------------------
# 1) 회사 로고
# ---------------------------------------------------
def parse_logo(soup):
    logo_tag = soup.find("img", src=lambda v: v and "upload/img/corp" in v)

    if logo_tag:
        src = logo_tag["src"]
        # 절대 경로로 변환
        if src.startswith("http"):
            return src
        return BASE_URL + src.lstrip(".")

    return None


# ---------------------------------------------------
# 2) 업종
# ---------------------------------------------------
def parse_sector(soup):
    sector_tag = soup.find("td", {"align": "right", "valign": "bottom"})
    return sector_tag.get_text(strip=True) if sector_tag else None


# ---------------------------------------------------
# 3) 공모가격 테이블 (가격 정보)
# ---------------------------------------------------
def parse_price_table(soup):
    """
    (희망)공모가격 ~ 청약경쟁률 구간을 파싱
    왼쪽 td(bgcolor=F0F0F0) = 항목명
    오른쪽 td = 값
    """
    price_info = {}

    for td in soup.find_all("td", bgcolor="F0F0F0"):
        key = td.get_text(strip=True).replace("\xa0", "")
        next_td = td.find_next_sibling("td")
        if next_td:
            value = next_td.get_text(strip=True).replace("\xa0", " ")
            price_info[key] = value

    return price_info


# ---------------------------------------------------
# 4) 공모주식수 테이블
# ---------------------------------------------------
def parse_share_table(soup):
    """
    '공모주식수'가 포함된 view_tb 테이블만 선택
    """
    tables = soup.find_all("table", class_="view_tb")
    for table in tables:
        first_row = table.find("tr")
        if not first_row:
            continue

        header = first_row.get_text(strip=True)
        if "공모주식수" in header:
            rows = []
            for tr in table.find_all("tr"):
                row = [td.get_text(strip=True).replace("\xa0", " ")
                       for td in tr.find_all("td")]
                if row:
                    rows.append(row)
            return rows

    return []


# ---------------------------------------------------
# 5) 증권사 배정 테이블
# ---------------------------------------------------
def parse_broker_table(soup):
    """
    header row의 첫 번째 셀이 '증권회사'인 테이블 찾기
    """
    tables = soup.find_all("table", {"class": "view_tb"})

    for table in tables:
        first_row = table.find("tr")
        if not first_row:
            continue

        headers = [td.get_text(strip=True) for td in first_row.find_all("td")]

        if "증권회사" in headers:
            rows = []
            trs = table.find_all("tr")[1:]  # header 제외
            for tr in trs:
                tds = [td.get_text(strip=True).replace("\xa0", " ") for td in tr.find_all("td")]
                rows.append(tds)
            return rows

    return []


# ---------------------------------------------------
# 전체 상세페이지 크롤링
# ---------------------------------------------------
def crawl_detail(url: str):
    soup = fetch_detail_page(url)

    return {
        "logo": parse_logo(soup),
        "업종": parse_sector(soup),
        "공모가격": parse_price_table(soup),
        "공모주식수": parse_share_table(soup),
        "증권사배정": parse_broker_table(soup),
    }


# ---------------------------------------------------
# TEST
# ---------------------------------------------------
if __name__ == "__main__":
    test_url = "http://www.ipostock.co.kr/view_pg/view_04.asp?code=B202506111&gmenu="
    from pprint import pprint
    pprint(crawl_detail(test_url))