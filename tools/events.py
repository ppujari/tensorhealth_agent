"""
Upcoming Events section.

Finds upcoming AI meetups and conferences in the next 6 months.
"""

# Default sources for AI events
DEFAULT_LISTING = "https://www.eventbrite.com/d/online/ai/"
DEFAULT_FALLBACK = "https://www.meetup.com/topics/ai/"


def build_research_prompt(section_key="th_events",
                          listing_url=None,
                          fallback_url=None):
    primary = listing_url or DEFAULT_LISTING
    fallback = fallback_url or DEFAULT_FALLBACK

    return (
        f"Find exactly 3 upcoming AI-related events (meetups, conferences, webinars) in the next 6 months.\n\n"
        f"STRICT WORKFLOW (do not deviate, do not guess URLs):\n"
        f"1. Call fetch_url on: {primary}\n"
        f"2. From the fetched text, identify the 3 MOST UPCOMING events "
        f"(events are listed by date). Each event should be in AI/ML space, "
        f"and scheduled within the next 6 months from today ({__import__('datetime').datetime.now().strftime('%Y-%m-%d')}). "
        f"Look for event titles, dates, and links of the form "
        f"'https://www.eventbrite.com/e/<id>' or similar.\n"
        f"3. If needed, call fetch_url on up to 2 individual event URLs to get full details.\n"
        f"4. Call save_section_draft with section_key='{section_key}' "
        f"and exactly 3 items.\n\n"
        f"Each item must have:\n"
        f"- title: event title verbatim\n"
        f"- summary: 2 sentences under 50 words total. "
        f"Sentence 1 = event date, location/format (online/in-person). "
        f"Sentence 2 = brief description of what the event covers.\n"
        f"- url: the event URL you fetched or extracted\n"
        f"- source: 'Eventbrite' or 'Meetup' etc.\n\n"
        f"ABSOLUTE RULES:\n"
        f"- Maximum 4 fetch_url calls total.\n"
        f"- Only include events in the AI space (machine learning, deep learning, AI applications).\n"
        f"- If the primary fetch returns few or no events, call fetch_url "
        f"ONCE on this fallback and pick 3 events from it: {fallback}\n"
        f"- NEVER guess or invent URLs. Only fetch URLs that appeared in "
        f"a page you already fetched, or the two URLs listed above.\n"
        f"- Skip events that are more than 6 months away.\n"
        f"- After save_section_draft, stop immediately."
    )