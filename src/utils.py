import json
from pathlib import Path
from datetime import datetime
import random


def shuffle(value):
    try:
        shuffled = list(value)  # Make a copy
        random.shuffle(shuffled)
        return shuffled
    except Exception:
        return value  # fallback if value is not iterable


def format_us_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%b %d, %Y")  # "Dec 27, 2023"
    except Exception:
        return date_str


def load_merged_routes():
    default_path = Path(__file__).parent / "routes.json"
    custom_path = Path(__file__).parent.parent / "routes.json"

    default_routes = []
    custom_routes = []

    if default_path.exists():
        default_routes = json.loads(default_path.read_text(encoding="utf-8"))
    if custom_path.exists():
        custom_routes = json.loads(custom_path.read_text(encoding="utf-8"))

    # Combine and deduplicate
    merged = sorted(set(default_routes + custom_routes))
    return merged


def load_merged_data():
    default_path = Path(__file__).parent / "data.json"
    custom_path = Path(__file__).parent.parent / "data.json"

    default_data = {}
    custom_data = {}

    if default_path.exists():
        default_data = json.loads(default_path.read_text(encoding="utf-8"))
    if custom_path.exists():
        custom_data = json.loads(custom_path.read_text(encoding="utf-8"))

    # Shallow merge: custom overrides default
    return {**default_data, **custom_data}
