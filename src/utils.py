import json
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
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


def format_date_range(start_str, end_str):
    start = datetime.strptime(start_str, "%m/%Y")
    end = datetime.strptime(end_str, "%m/%Y")

    diff = relativedelta(end, start)
    years = diff.years
    months = diff.months

    start_fmt = start.strftime("%b %Y")  # e.g. "Feb 2024"
    end_fmt = end.strftime("%b %Y")  # e.g. "Jun 2025"

    parts = []
    if years == 1:
        parts.append("1 yr")
    elif years > 1:
        parts.append(f"{years} yrs")
    if months == 1:
        parts.append("1 mo")
    elif months > 1:
        parts.append(f"{months} mos")

    duration = " ".join(parts)
    return f"{start_fmt} - {end_fmt} · {duration}"


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
