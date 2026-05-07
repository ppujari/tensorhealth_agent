"""
News bits and bytes section.

Works for both newsletters:
  TensorHealth: section_key='th_news_bits'  (medical-AI news)
  AYNA:         section_key='ayna_news_bits' (LLM agent news)

Strategy:
  1. Fetch multiple RSS feeds locally (Python, not agent fetch_url)
  2. Extract title + description + link from each <item>
  3. Pass all items to Claude as text
  4. Claude picks the top 10-15 most relevant, writes 2-3 line blurbs
  5. save_section_draft with all items

Total fetch_url calls: 0 (all done pre-agent).
"""

import os
import time
import requests
from xml.etree import ElementTree as ET
from config import FETCH_DELAY_SECONDS

# --- RSS Feed Sources ---
# Grouped by newsletter. Each feed has a name and URL.

AYNA_FEEDS = [
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("OpenAI Blog", "https://openai.com/blog/rss.xml"),
]

TENSORHEALTH_FEEDS = [
    ("STAT News", "https://www.statnews.com/feed/"),
    ("Fierce Healthcare", "https://www.fiercehealthcare.com/rss/xml"),
    ("MobiHealthNews", "https://www.mobihealthnews.com/feed"),
    ("Healthcare IT News", "https://www.healthcareitnews.com/feed"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def _fetch_feed(name, url):
    """Fetch a single RSS/Atom feed and return parsed items."""
    items = []
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ! {name}: {type(e).__name__}")
        return items

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        print(f"    ! {name}: XML parse error")
        return items

    # Handle both RSS 2.0 (<item>) and Atom (<entry>) formats
    # RSS 2.0
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        if title and link:
            # Strip HTML tags from description
            import re
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:300]
            items.append({
                "feed": name,
                "title": title,
                "link": link,
                "description": desc_clean,
                "date": pub_date,
            })

    # Atom format (namespace handling)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        summary_el = entry.find("atom:summary", ns)
        updated_el = entry.find("atom:updated", ns)

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.get("href", "") if link_el is not None else ""
        desc = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
        date = updated_el.text.strip() if updated_el is not None and updated_el.text else ""

        if title and link:
            import re
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:300]
            items.append({
                "feed": name,
                "title": title,
                "link": link,
                "description": desc_clean,
                "date": date,
            })

    return items[:10]  # Cap per feed to avoid prompt bloat


def _gather_all_feeds(feeds):
    """Fetch all feeds and return combined items."""
    all_items = []
    for name, url in feeds:
        print(f"    fetching {name}...")
        items = _fetch_feed(name, url)
        all_items.extend(items)
        time.sleep(FETCH_DELAY_SECONDS)
    return all_items


def _format_items_for_prompt(items):
    """Format items as numbered text for the prompt."""
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(
            f"{i}. [{item['feed']}] {item['title']}\n"
            f"   {item['description']}\n"
            f"   Link: {item['link']}\n"
            f"   Date: {item['date']}"
        )
    return "\n\n".join(lines)


def build_research_prompt(section_key="ayna_news_bits"):
    """
    Fetch RSS feeds, format items, and build the prompt.
    Returns a string prompt or None if no items found.
    """
    # Pick the right feed list based on newsletter
    if section_key.startswith("th_"):
        feeds = TENSORHEALTH_FEEDS
        topic = "medical AI and healthcare technology"
    else:
        feeds = AYNA_FEEDS
        topic = "LLM agents, AI agents, large language models, and AI tools"

    print(f"  gathering RSS feeds ({len(feeds)} sources)...")
    all_items = _gather_all_feeds(feeds)

    if not all_items:
        print(f"  ! no items found from any feed — skipping News")
        return None

    print(f"  ✓ collected {len(all_items)} items total")
    formatted = _format_items_for_prompt(all_items)

    return (
        f"You are curating the 'News bits and bytes' section of a newsletter "
        f"about {topic}.\n\n"
        f"Below are {len(all_items)} news items gathered from multiple RSS feeds. "
        f"Your job is to pick the 10 to 15 MOST relevant and interesting items "
        f"about {topic}.\n\n"
        f"--- NEWS ITEMS ---\n"
        f"{formatted}\n"
        f"--- END ---\n\n"
        f"Call save_section_draft with section_key='{section_key}' and "
        f"10 to 15 items.\n\n"
        f"Each item must have:\n"
        f"- title: the original headline (keep it short, trim if needed)\n"
        f"- summary: 2-3 sentences maximum. What happened and why it matters. "
        f"Keep each summary under 40 words. Be crisp and factual.\n"
        f"- url: the original article link from the feed\n"
        f"- source: the feed name (e.g. 'The Verge', 'TechCrunch')\n\n"
        f"RULES:\n"
        f"- Do NOT call fetch_url. All content is above.\n"
        f"- Only include items clearly related to {topic}. Skip unrelated items.\n"
        f"- Prefer recency — newer items first.\n"
        f"- Do NOT invent headlines or URLs. Use exactly what's in the list.\n"
        f"- If fewer than 10 relevant items exist, include however many you find.\n"
        f"- After save_section_draft, stop immediately."
    )
