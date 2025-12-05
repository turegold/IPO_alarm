# services/settings_service.py

from pathlib import Path
import json

SETTINGS_PATH = Path("data") / "settings.json"


def load_webhook_url() -> str:
    """settings.json에서 디스코드 웹훅 URL 불러오기"""
    if not SETTINGS_PATH.exists():
        return ""

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("webhook_url", "")
    except:
        return ""


def save_webhook_url(url: str):
    """웹훅 URL 저장"""
    SETTINGS_PATH.parent.mkdir(exist_ok=True)

    data = {
        "webhook_url": url
    }

    with SETTINGS_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)