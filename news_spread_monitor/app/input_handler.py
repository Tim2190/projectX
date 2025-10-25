"""Handle user input for news spread monitoring"""

import requests
from bs4 import BeautifulSoup
from typing import Tuple


def parse_input(user_input: str) -> Tuple[str, str]:
    """Detect if input is a URL or plain text and return cleaned text and url."""
    user_input = user_input.strip()
    if user_input.startswith("http://") or user_input.startswith("https://"):
        try:
            resp = requests.get(user_input, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string if soup.title else ""
            paragraphs = " ".join(p.get_text() for p in soup.find_all("p"))
            return f"{title} {paragraphs}", user_input
        except Exception:
            return user_input, user_input
    return user_input, ""
