"""
Top AI Hiring section.

Finds recent AI-related job openings in AI, RAG, agentic engineering, and data center buildout.
"""

DEFAULT_LISTING = "https://remoteok.com/remote-ai-jobs"
DEFAULT_FALLBACK = "https://weworkremotely.com/categories/remote-ai-jobs"


def build_research_prompt(section_key="th_hiring",
                          listing_url=None,
                          fallback_url=None):
    primary = listing_url or DEFAULT_LISTING
    fallback = fallback_url or DEFAULT_FALLBACK

    return (
        f"Find exactly 3 recent AI-related job openings.\n\n"
        f"STRICT WORKFLOW (do not deviate, do not guess URLs):\n"
        f"1. Call fetch_url on: {primary}\n"
        f"2. From the fetched text, identify the 3 MOST RECENT job postings. "
        f"Each job should be in AI/ML space, "
        f"including RAG, agentic engineering, data center buildout, or related fields. "
        f"Extract job titles, companies, and their direct URLs from the page.\n"
        f"3. If needed, call fetch_url on up to 2 individual job URLs to get full details.\n"
        f"4. Call save_section_draft with section_key='{section_key}' "
        f"and exactly 3 items.\n\n"
        f"Each item must have:\n"
        f"- title: job title + company name verbatim\n"
        f"- summary: 2 sentences under 50 words total. "
        f"Sentence 1 = job location, type (remote/on-site), salary if mentioned. "
        f"Sentence 2 = brief description of responsibilities and requirements.\n"
        f"- url: the job posting URL you fetched or extracted\n"
        f"- source: the job board name (e.g. 'RemoteOK', 'We Work Remotely')\n\n"
        f"ABSOLUTE RULES:\n"
        f"- Maximum 4 fetch_url calls total.\n"
        f"- Only include jobs in AI, RAG, agentic engineering, data center, or closely related fields.\n"
        f"- If the primary fetch returns few or no jobs, call fetch_url "
        f"ONCE on this fallback: {fallback}\n"
        f"- NEVER guess or invent URLs. Only use URLs that appeared in "
        f"a page you already fetched, or the two URLs listed above.\n"
        f"- After save_section_draft, stop immediately."
    )
