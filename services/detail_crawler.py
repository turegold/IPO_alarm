# IPO Stock 공모주 상세 페이지를 크롤링하여
# 회사 로고, 업종, 공모가격, 공모주식 수, 증권사별 정보 등을 구조화된 데이터로 추출하는 크롤러


import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.ipostock.co.kr"


# 공모주 상세 페이지 HTML을 요청하고, BeautifulSoup 객체로 변환해 반환하는 함수
def fetch_detail_page(url: str):
    res = requests.get(url)
    res.encoding = "utf-8"
    return BeautifulSoup(res.text, "html.parser")



# 상세 페이지에서 회사 로고 이미지 URL을 추출하는 함수
def parse_logo(soup):
    logo_tag = soup.find("img", src=lambda v: v and "upload/img/corp" in v)

    if logo_tag:
        src = logo_tag["src"]
        # 절대 경로로 변환
        if src.startswith("http"):
            return src
        return BASE_URL + src.lstrip(".")

    return None


# 기업의 업종 정보를 파싱하는 함수
def parse_sector(soup):
    sector_tag = soup.find("td", {"align": "right", "valign": "bottom"})
    return sector_tag.get_text(strip=True) if sector_tag else None


# (희망)공모가격, (확장)공모가격, 청약 경쟁률 등의 정보를 추출하는 함수
def parse_price_table(soup):
    price_info = {}

    for td in soup.find_all("td", bgcolor="F0F0F0"):
        key = td.get_text(strip=True).replace("\xa0", "")
        next_td = td.find_next_sibling("td")
        if next_td:
            value = next_td.get_text(strip=True).replace("\xa0", " ")
            price_info[key] = value

    return price_info


# '공모주식수'가 포함된 테이블을 찾아 데이터를 추출하는 함수
def parse_share_table(soup):
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


# '증권회사'가 있는 테이블을 찾아 데이터를 추출하는 함수
def parse_broker_table(soup):
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


# 위의 모든 파싱 함수를 호출해 상세 페이지의 핵심 정보를 하나의 딕셔너리로 통합하여 반환하는 함수
def crawl_detail(url: str):
    soup = fetch_detail_page(url)

    return {
        "logo": parse_logo(soup),
        "업종": parse_sector(soup),
        "공모가격": parse_price_table(soup),
        "공모주식수": parse_share_table(soup),
        "증권사배정": parse_broker_table(soup),
    }



if __name__ == "__main__":
    test_url = "http://www.ipostock.co.kr/view_pg/view_04.asp?code=B202506111&gmenu="
    from pprint import pprint
    pprint(crawl_detail(test_url))