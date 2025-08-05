import json
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import htmlmin
import re
from dotenv import load_dotenv


def reload_env_vars():
    load_dotenv(dotenv_path="/.env", override=True)


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


def format_date_range(start_str, end_str=None):
    start = datetime.strptime(start_str, "%m/%Y")

    # If end_str is None or empty, use current date
    if not end_str:
        end = datetime.now()
        end_fmt = "Present"
    else:
        end = datetime.strptime(end_str, "%m/%Y")
        end_fmt = end.strftime("%b %Y")

    diff = relativedelta(end, start)
    years = diff.years
    months = diff.months

    start_fmt = start.strftime("%b %Y")  # e.g. "Feb 2024"

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


def minify_html(html: str) -> str:
    # Step 1: Minify using htmlmin
    html = htmlmin.minify(
        html,
        remove_comments=True,
        remove_empty_space=True,
        remove_all_empty_space=True,
        reduce_empty_attributes=True,
        reduce_boolean_attributes=True,
        remove_optional_attribute_quotes=True,
        keep_pre=False
    )

    # Step 2: Normalize attribute values — collapse inner whitespace and strip leading/trailing
    def clean_attr_value(match):
        attr = match.group(1)
        quote = match.group(2)
        value = match.group(3)
        cleaned = re.sub(r'\s+', ' ', value).strip()
        return f'{attr}={quote}{cleaned}{quote}'

    # This handles key="value with   spaces\nand lines"
    html = re.sub(r'(\w+)=([\'"])(.*?)\2', clean_attr_value, html, flags=re.DOTALL)

    return html.strip()
