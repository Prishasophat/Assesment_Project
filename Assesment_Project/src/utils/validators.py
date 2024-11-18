import re
from typing import Optional

def validate_sheet_url(url: str) -> bool:
    pattern = r'^https://docs\.google\.com/spreadsheets/d/[a-zA-Z0-9-_]+(/edit#gid=[0-9]+)?$'
    return bool(re.match(pattern, url))

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
