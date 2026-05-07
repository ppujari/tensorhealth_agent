"""
Emerging Trends section.

Works for both newsletters:
  TensorHealth: section_key='th_emerging_trends'
  AYNA:         section_key='ayna_emerging_trends'

Strategy:
  This section is SYNTHESIS — it reads everything the agent has
  already collected from other sections and identifies 2-3
  forward-looking trends. No fetch_url calls needed.

  We also fetch 1-2 research-focused RSS feeds for additional
  signal about where the field is heading.
"""

import time
import re
import requests
from xml.etree import ElementTree as ET
from config import FETCH_DELAY_SECONDS

AYNA_FEEDS = [
    ("Lilian Weng (OpenAI)", "https://lilianweng.github.io/index.xml"),
    ("The Batch (Andrew Ng)", "https://www.deeplearning.ai/the-batch/feed/"),
    ("Anthropic Research", "https://www.anthropic.com/research/rss.xml"),
]

TENSORHEALTH_FEEDS = [
    ("Google Health AI", "https://blog.google/technology/health/rss/"),
    ("NEJM AI", "https://ai.nejm.org/action/showFeed?type=etoc&feed=rss&jc=ai"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def _fetch_feed(name, url):
    """Fetch RSS/Atom feed and return items."""
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

    # RSS 2.0
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "").strip()
        if title and link:
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:200]
            items.append(f"[{name}] {title} — {desc_clean} ({link})")

    # Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        summary_el = entry.find("atom:summary", ns)
        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.get("href", "") if link_el is not None else ""
        desc = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
        if title and link:
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:200]
            items.append(f"[{name}] {title} — {desc_clean} ({link})")

    return items[:5]


def _gather_feeds(feeds):
    all_items = []
    for name, url in feeds:
        print(f"    fetching {name}...")
        items = _fetch_feed(name, url)
        all_items.extend(items)
        time.sleep(FETCH_DELAY_SECONDS)
    return all_items


def build_research_prompt(section_key="ayna_emerging_trends",
                          already_collected=None):
    """
    Build prompt using already-collected sections + research feeds.

    Args:
        section_key: the section identifier
        already_collected: dict of section_key -> items from earlier
                          sections (used for synthesis)
    """
    # Pick feeds based on newsletter
    if section_key.startswith("th_"):
        feeds = TENSORHEALTH_FEEDS
        topic = "medical AI and healthcare technology"
    else:
        feeds = AYNA_FEEDS
        topic = "LLM agents, AI agents, and AI infrastructure"

    # Gather research feeds
    print(f"  gathering research feeds ({len(feeds)} sources)...")
    feed_items = _gather_feeds(feeds)
    feed_text = "\n".join(feed_items) if feed_items else "(no feed items)"
    print(f"  ✓ collected {len(feed_items)} research items")

    # Summarize what was already collected from other sections
    prior_text = ""
    if already_collected:
        lines = []
        for sk, items in already_collected.items():
            for item in items:
                lines.append(f"- {item.get('title', '')} ({item.get('source', '')})")
        prior_text = "\n".join(lines)

    prior_block = ""
    if prior_text:
        prior_block = (
            f"\n--- ITEMS FROM OTHER SECTIONS THIS WEEK ---\n"
            f"{prior_text}\n"
            f"--- END ---\n"
        )

    return (
        f"You are writing the 'Emerging Trends' section of a newsletter "
        f"about {topic}. This section looks FORWARD — it identifies "
        f"where the technology is heading in the next 2-3 years.\n\n"
        f"Use the research blog posts and the items already collected "
        f"from other sections to identify 2-3 emerging trends.\n\n"
        f"--- RESEARCH BLOG POSTS ---\n"
        f"{feed_text}\n"
        f"--- END ---\n"
        f"{prior_block}\n"
        f"Call save_section_draft with section_key='{section_key}' "
        f"and 2 to 3 items.\n\n"
        f"Each item must have:\n"
        f"- title: a short trend name (e.g. 'Agentic RAG is replacing "
        f"static retrieval', 'Multi-modal models enter clinical trials')\n"
        f"- summary: 3-4 sentences. What is the trend? What evidence "
        f"supports it from this week's news/research? Where does it lead "
        f"in 2-3 years? Under 80 words.\n"
        f"- url: link to the most relevant source that supports this trend "
        f"(from the feeds or prior sections above)\n"
        f"- source: the publication name\n\n"
        f"RULES:\n"
        f"- Do NOT call fetch_url. All content is above.\n"
        f"- Each trend must be grounded in at least one item above — "
        f"no pure speculation.\n"
        f"- Focus on forward-looking directions, not just this week's news.\n"
        f"- After save_section_draft, stop immediately."
    )
