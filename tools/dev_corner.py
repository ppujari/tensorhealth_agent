"""
Developers' Corner / Clinical Code Lab section.

Works for both newsletters:
  TensorHealth: section_key='th_code_lab'  (Clinical Code Lab)
  AYNA:         section_key='ayna_dev_corner' (Developers' Corner)

Source: RSS feeds from tutorial-focused publications + GitHub.
Strategy:
  1. Fetch tutorial-focused RSS feeds in Python (pre-agent)
  2. Search GitHub API for trending tutorial/cookbook repos
  3. Pass everything to Claude
  4. Claude picks 2-3 best tutorials with hands-on coding focus

Zero fetch_url calls during agent loop.
"""

import re
import time
import requests
from xml.etree import ElementTree as ET
from config import FETCH_DELAY_SECONDS

AYNA_FEEDS = [
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("LangChain Blog", "https://blog.langchain.dev/rss/"),
    ("dev.to #ai", "https://dev.to/feed/tag/ai"),
    ("dev.to #llm", "https://dev.to/feed/tag/llm"),
]

TENSORHEALTH_FEEDS = [
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
    ("dev.to #machinelearning", "https://dev.to/feed/tag/machinelearning"),
    ("Towards Data Science", "https://towardsdatascience.com/feed"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

_GH_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "TensorHealth-Newsletter-Agent",
}


def _fetch_feed(name, url):
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
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:250]
            items.append({
                "source": name,
                "title": title,
                "link": link,
                "description": desc_clean,
            })

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
            desc_clean = re.sub(r"<[^>]+>", "", desc)[:250]
            items.append({
                "source": name,
                "title": title,
                "link": link,
                "description": desc_clean,
            })

    return items[:8]


def _search_github_tutorials(topic_query):
    """Search GitHub for tutorial/cookbook repos."""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": topic_query,
        "sort": "updated",
        "order": "desc",
        "per_page": 5,
    }
    try:
        resp = requests.get(url, headers=_GH_HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as e:
        print(f"    ! GitHub tutorials: {e}")
        return []

    repos = []
    for item in data.get("items", []):
        repos.append({
            "source": "GitHub",
            "title": item.get("full_name", ""),
            "link": item.get("html_url", ""),
            "description": item.get("description", "") or "",
        })
    return repos


def _format_items(items):
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(
            f"{i}. [{item['source']}] {item['title']}\n"
            f"   {item['description']}\n"
            f"   Link: {item['link']}"
        )
    return "\n\n".join(lines)


def build_research_prompt(section_key="ayna_dev_corner"):
    # Pick feeds and GitHub query based on newsletter
    if section_key.startswith("th_"):
        feeds = TENSORHEALTH_FEEDS
        gh_query = "medical AI tutorial cookbook language:python stars:>20"
        topic = "medical AI, clinical ML, and healthcare data science"
        section_name = "Clinical Code Lab"
    else:
        feeds = AYNA_FEEDS
        gh_query = "LLM agent tutorial cookbook language:python stars:>20"
        topic = "LLM agents, prompt engineering, tool-use, and agentic AI"
        section_name = "Developers' Corner"

    # Fetch RSS feeds
    all_items = []
    print(f"  gathering tutorial feeds ({len(feeds)} sources)...")
    for name, url in feeds:
        print(f"    fetching {name}...")
        items = _fetch_feed(name, url)
        all_items.extend(items)
        time.sleep(FETCH_DELAY_SECONDS)

    # Fetch GitHub tutorials
    print(f"    searching GitHub tutorials...")
    gh_repos = _search_github_tutorials(gh_query)
    all_items.extend(gh_repos)

    if not all_items:
        print(f"  ! no items found — skipping {section_name}")
        return None

    print(f"  ✓ collected {len(all_items)} tutorial items total")
    formatted = _format_items(all_items)

    return (
        f"You are curating the '{section_name}' section of a newsletter "
        f"about {topic}. This section is about HANDS-ON TUTORIALS — "
        f"posts and repos where readers can learn by coding.\n\n"
        f"Below are {len(all_items)} items from tutorial-focused sources.\n\n"
        f"--- TUTORIAL ITEMS ---\n"
        f"{formatted}\n"
        f"--- END ---\n\n"
        f"Call save_section_draft with section_key='{section_key}' "
        f"and 2 to 3 items.\n\n"
        f"Selection criteria:\n"
        f"- MUST be a tutorial, guide, cookbook, or hands-on walkthrough "
        f"with actual code. Skip pure news, opinion, or announcements.\n"
        f"- Prefer beginner-to-intermediate level that teaches core concepts.\n"
        f"- Prefer recent posts over older ones.\n\n"
        f"Each item must have:\n"
        f"- title: the tutorial title\n"
        f"- summary: 2-3 sentences. What will the reader learn? What do "
        f"they build? What concepts does it cover? Under 50 words.\n"
        f"- url: the link from the list above\n"
        f"- source: the publication name from the list above\n\n"
        f"RULES:\n"
        f"- Do NOT call fetch_url. All info is above.\n"
        f"- ONLY select items that are genuinely tutorials with code.\n"
        f"- Use URLs exactly as listed. Do not guess.\n"
        f"- After save_section_draft, stop immediately."
    )
