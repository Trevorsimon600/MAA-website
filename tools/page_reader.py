import requests
from bs4 import BeautifulSoup
from typing import Optional

def read_page(url: str, max_chars: int = 3000) -> str:
    """
    Read the main text content of a webpage.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + "\n\n[Content truncated...]"

        return clean_text if clean_text else "No readable content found."

    except Exception as e:
        return f"Failed to read page: {str(e)}"