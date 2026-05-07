"""
Agent Showcase section (AYNA only).

Source: GitHub REST API (api.github.com).
Strategy:
  1. Search GitHub API for recently updated agent repos (Python, no auth)
  2. Format results and pass to Claude
  3. Claude picks the most interesting one and summarizes
  4. Zero fetch_url calls during agent loop

GitHub API allows 60 requests/hour unauthenticated — more than enough.
"""

import requests
from config import FETCH_DELAY_SECONDS

SECTION_KEY = "ayna_showcase"

_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "TensorHealth-Newsletter-Agent",
}

# Search queries — tried in order until one returns results
SEARCH_QUERIES = [
    "agent LLM language:python stars:>50 pushed:>2026-03-01",
    "agentic AI framework language:python stars:>100",
    "multi-agent LLM stars:>50",
]


def _search_github(query, max_results=15):
    """Call GitHub search API and return formatted repo list."""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": max_results,
    }
    try:
        resp = requests.get(url, headers=_HEADERS, params=params, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    ! GitHub API: {type(e).__name__}: {e}")
        return []

    data = resp.json()
    repos = []
    for item in data.get("items", []):
        repos.append({
            "name": item.get("full_name", ""),
            "url": item.get("html_url", ""),
            "description": item.get("description", "") or "",
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language", ""),
            "updated": item.get("updated_at", ""),
            "topics": item.get("topics", []),
        })
    return repos


def _format_repos(repos):
    """Format repos as text for the prompt."""
    lines = []
    for i, r in enumerate(repos, 1):
        topics = ", ".join(r["topics"][:5]) if r["topics"] else "none"
        lines.append(
            f"{i}. {r['name']} — ⭐ {r['stars']}\n"
            f"   {r['description']}\n"
            f"   Topics: {topics}\n"
            f"   Updated: {r['updated']}\n"
            f"   URL: {r['url']}"
        )
    return "\n\n".join(lines)


def build_research_prompt(section_key=None):
    key = section_key or SECTION_KEY

    # Try each query until one returns results
    repos = []
    for query in SEARCH_QUERIES:
        print(f"    searching GitHub: {query[:50]}...")
        repos = _search_github(query)
        if repos:
            break

    if not repos:
        print(f"  ! no repos found from GitHub API — skipping Showcase")
        return None

    print(f"  ✓ found {len(repos)} repos")
    formatted = _format_repos(repos)

    return (
        f"Pick 1 interesting open-source AI agent project to showcase "
        f"from the list below.\n\n"
        f"--- GITHUB REPOS ---\n"
        f"{formatted}\n"
        f"--- END ---\n\n"
        f"Call save_section_draft with section_key='{key}' "
        f"and exactly 1 item.\n\n"
        f"Selection criteria:\n"
        f"- Must be about LLM agents, AI agents, agent frameworks, "
        f"tool-use, multi-agent systems, MCP, or agentic workflows.\n"
        f"- Prefer newer or less well-known projects over established "
        f"ones like LangChain, AutoGen, or CrewAI.\n"
        f"- Prefer repos with clear descriptions and active development.\n\n"
        f"The item must have:\n"
        f"- title: 'repo-name — one-line description'\n"
        f"- summary: 3-4 sentences. What does it do? What problem does it "
        f"solve? Why is it interesting for agent builders? Under 80 words.\n"
        f"- url: the GitHub repo URL from the list\n"
        f"- source: 'GitHub'\n\n"
        f"RULES:\n"
        f"- Do NOT call fetch_url. All info is above.\n"
        f"- ALWAYS pick exactly 1 repo. Never return 0 items.\n"
        f"- Use the URL exactly as listed. Do not guess.\n"
        f"- After save_section_draft, stop immediately."
    )
