"""
Opinion AI section.

Works for both newsletters:
  TensorHealth: section_key='th_opinion'
  AYNA:         section_key='ayna_opinion'

Source: Pradeep Pujari's Medium RSS feed.
Full article text is in <content:encoded> — no second fetch needed.
"""

MEDIUM_FEED = "https://ppujari.medium.com/feed"


def build_research_prompt(section_key="th_opinion"):
    return (
        f"Find the author's latest Medium blog post for the Opinion section.\n\n"
        f"STRICT WORKFLOW:\n"
        f"1. Call fetch_url ONCE on: {MEDIUM_FEED}\n"
        f"   This returns RSS/XML. Look for <item> blocks. Each has:\n"
        f"   - <title>...post title...</title>\n"
        f"   - <link>...post URL...</link>\n"
        f"   - <content:encoded>...FULL article text...</content:encoded>\n"
        f"2. Pick the FIRST <item> (it is the most recent post).\n"
        f"3. Read the article text from <content:encoded> — do NOT "
        f"try to fetch the Medium article URL (it will return 403).\n"
        f"4. Call save_section_draft with section_key='{section_key}' "
        f"and exactly 1 item.\n\n"
        f"The item must have:\n"
        f"- title: the post title from <title>\n"
        f"- summary: 3-4 sentence summary of the post's key argument. "
        f"Written in third person ('The author argues...'). Under 80 words.\n"
        f"- url: the Medium post URL from <link>\n"
        f"- source: 'Medium'\n\n"
        f"RULES:\n"
        f"- Only 1 fetch_url call. Do NOT fetch the article page.\n"
        f"- ALWAYS pick a post, even if it is old.\n"
        f"- NEVER invent titles or URLs.\n"
        f"- After save_section_draft, stop immediately."
    )
