import json
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import htmlmin
import re
from dotenv import load_dotenv


def reload_env_vars():
    load_dotenv(dotenv_path="../.env", override=True)


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


def parse_date(date_str):
    """Parse a date string and return (datetime_obj, has_day_flag)."""
    for fmt in ("%m/%d/%Y", "%m/%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            has_day = fmt == "%m/%d/%Y"
            return dt, has_day
        except ValueError:
            continue
    raise ValueError(f"Date '{date_str}' is not in a supported format (expected mm/YYYY or mm/dd/YYYY)")


def format_date_range(start_str, end_str=None):
    start, start_has_day = parse_date(start_str)

    if not end_str:
        end = datetime.now()
        end_fmt = "Present"
        end_has_day = False
    else:
        end, end_has_day = parse_date(end_str)
        end_fmt = end.strftime("%b %-d, %Y") if end_has_day else end.strftime("%b %Y")

    # Adjust for month-only dates like LinkedIn
    adj_end = end
    if not start_has_day or not end_has_day:
        # Add one month to make duration inclusive
        adj_end += relativedelta(days=31)  # add enough days to cover one month
    diff = relativedelta(adj_end, start)

    years = diff.years
    months = diff.months

    start_fmt = start.strftime("%b %-d, %Y") if start_has_day else start.strftime("%b %Y")

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
    routes = {
        "/": "index.html"
    }

    custom_path = Path(__file__).parent / "routes.json"
    if custom_path.exists():
        routes.update(json.loads(custom_path.read_text(encoding="utf-8")))

    return routes


def load_merged_data():
    data = {}

    custom_path = Path(__file__).parent / "data.json"
    if custom_path.exists():
        data.update(json.loads(custom_path.read_text(encoding="utf-8")))

    return data


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


def unique(value):
    if isinstance(value, list):
        return list(dict.fromkeys(value))
    return value
