# services/ipo_loader.py

from pathlib import Path
import json


DATA_DIR = Path("data")


def load_ipo_list(year: int, month: int):
    path = DATA_DIR / f"ipo_{year}_{month:02d}.json"
    if not path.exists():
        return []
    try:
        return json.load(path.open("r", encoding="utf-8"))
    except:
        return []


def load_completed_names():
    path = DATA_DIR / "completed.json"
    if not path.exists():
        return set()
    try:
        data = json.load(path.open("r", encoding="utf-8"))
        return {d.get("종목명") for d in data}
    except:
        return set()


def load_subscribe_names():
    path = DATA_DIR / "subscribe.json"
    if not path.exists():
        return set()
    try:
        data = json.load(path.open("r", encoding="utf-8"))
        return {d.get("종목명") for d in data}
    except:
        return set()