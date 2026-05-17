"""
Tool schemas sent to the Groq API (OpenAI-compatible format).

Two custom tools:
  1. fetch_url           — fetches a URL and returns extracted text
  2. save_section_draft  — agent hands us curated items per section

The agent works from a curated list of URLs defined in config.py,
which is cheaper, more deterministic, and avoids rate limits.
"""

FETCH_URL_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_url",
        "description": (
            "Fetch a single web page and return its extracted text. "
            "Use this to read listing pages (Google Scholar profiles, "
            "lab publication pages, RSS feeds) and then to read the "
            "individual paper/article pages linked from those listings. "
            "Returns status, url, and text. Never makes up content — "
            "if a fetch fails, try another URL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch (must start with http:// or https://)",
                },
            },
            "required": ["url"],
        },
    },
}

SAVE_SECTION_DRAFT_TOOL = {
    "type": "function",
    "function": {
        "name": "save_section_draft",
        "description": (
            "Save a completed newsletter section. Call this exactly once "
            "per section after you've finished fetching and summarizing. "
            "Each item should have a short summary (2-4 sentences) and a "
            "URL for the 'Read more' button."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "section_key": {
                    "type": "string",
                    "description": "Identifier matching a key in config.SECTIONS",
                },
                "items": {
                    "type": "array",
                    "description": "The curated items for this section.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {
                                "type": "string",
                                "description": "2-4 sentence plain-English summary",
                            },
                            "url": {"type": "string"},
                            "source": {
                                "type": "string",
                                "description": "Publisher or venue (e.g. 'arXiv', 'Nature Medicine')",
                            },
                        },
                        "required": ["title", "summary", "url", "source"],
                    },
                },
            },
            "required": ["section_key", "items"],
        },
    },
}


def get_tools_for_run():
    """Return the tool list to pass to the Groq API for a run."""
    return [FETCH_URL_TOOL, SAVE_SECTION_DRAFT_TOOL]
