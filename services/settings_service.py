# 디스코드 알림에 사용되는 웹훅 URL을 settings.json 파일에 저장하고 불러오는 설정 관리 모듈

from pathlib import Path
import json

SETTINGS_PATH = Path("data") / "settings.json"

# settings.json에서 디스코드 웹훅 URL을 읽어서 반환하는 함수
def load_webhook_url() -> str:
    if not SETTINGS_PATH.exists():
        return ""

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("webhook_url", "")
    except:
        return ""

# 전달받은 웹훅 URL을 settings.json 파일에 저장하는 함수
def save_webhook_url(url: str):
    SETTINGS_PATH.parent.mkdir(exist_ok=True)

    data = {
        "webhook_url": url
    }

    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)