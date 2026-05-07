"""
URL fetcher.

Isolated module for the HTTP + HTML-to-text work. Keeping this
separate from the agent loop means we can swap implementations
later (e.g. add caching, proxies, or JS rendering) without
touching anything else.
"""

import time
import requests
from bs4 import BeautifulSoup

from config import FETCH_DELAY_SECONDS, MAX_PAGE_CHARS

# Use a real-browser User-Agent. Some sites (including Scholar)
# reject the default requests UA outright.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_last_fetch_time = 0.0


def _polite_wait():
    """Sleep if the previous fetch was too recent."""
    global _last_fetch_time
    elapsed = time.time() - _last_fetch_time
    if elapsed < FETCH_DELAY_SECONDS:
        time.sleep(FETCH_DELAY_SECONDS - elapsed)
    _last_fetch_time = time.time()


def _extract_text(html):
    """Strip HTML to readable text + keep link URLs visible."""
    soup = BeautifulSoup(html, "html.parser")

    # Drop noise
    for tag in soup(["script", "style", "noscript", "nav", "footer"]):
        tag.decompose()

    # Convert <a> tags to "text (url)" so the agent can see link targets
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if text and href.startswith("http"):
            a.replace_with(f"{text} ({href})")

    text = soup.get_text(separator="\n", strip=True)
    # Collapse runs of blank lines
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def fetch_url(url):
    """
    Fetch a URL and return extracted text + metadata.

    Returns a dict: {status, url, text, error}
    Never raises — errors come back in the 'error' field so the
    agent can see them and try another URL.
    """
    _polite_wait()
    try:
        response = requests.get(url, headers=_HEADERS, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        return {
            "status": "error",
            "url": url,
            "text": "",
            "error": f"{type(e).__name__}: {e}",
        }

    content_type = response.headers.get("Content-Type", "").lower()

    # Handle RSS/Atom feeds as plain text (no HTML stripping).
    # Check both Content-Type and common feed URL patterns.
    is_feed = (
        "xml" in content_type
        or "rss" in content_type
        or "atom" in content_type
        or url.endswith(("/feed", "/feed/", ".xml", ".rss", ".atom"))
        or "/feed" in url
    )
    if is_feed:
        text = response.text
    else:
        text = _extract_text(response.text)

    if len(text) > MAX_PAGE_CHARS:
        text = text[:MAX_PAGE_CHARS] + "\n\n[...truncated...]"

    # Treat near-empty pages as errors so the agent switches strategy
    # instead of guessing URLs from a blank response.
    if len(text.strip()) < 200:
        return {
            "status": "error",
            "url": url,
            "text": "",
            "error": (
                "page returned near-empty content "
                "(likely JavaScript-rendered or blocked) — "
                "use the fallback URL from the prompt"
            ),
        }

    return {
        "status": "ok",
        "url": url,
        "text": text,
        "error": None,
    }
