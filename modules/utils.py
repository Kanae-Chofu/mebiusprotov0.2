# modules/utils.py
import datetime
import re

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sanitize_message(text: str, max_len: int) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len]