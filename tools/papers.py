"""
Top Papers section.

Works for both newsletters with different sources:
  TensorHealth: Pranav Rajpurkar's arXiv (medical-AI)
  AYNA:         arXiv cs.AI/cs.CL/cs.MA (LLM agents)

The listing URL is passed in from main.py based on the newsletter config.
"""

# Defaults if no URL is passed
DEFAULT_LISTING = "https://arxiv.org/a/rajpurkar_p_1"
DEFAULT_FALLBACK = "https://arxiv.org/list/cs.CV/recent"


def build_research_prompt(section_key="th_top_papers",
                          listing_url=None,
                          fallback_url=None):
    primary = listing_url or DEFAULT_LISTING
    fallback = fallback_url or DEFAULT_FALLBACK

    return (
        f"Find exactly 2 recent AI papers and summarize them.\n\n"
        f"STRICT WORKFLOW (do not deviate, do not guess URLs):\n"
        f"1. Call fetch_url on: {primary}\n"
        f"2. From the fetched text, identify the 2 MOST RECENT papers "
        f"(papers are listed newest-first). Each paper has an arXiv ID "
        f"like '2504.12345' and a link of the form "
        f"'https://arxiv.org/abs/<id>'.\n"
        f"3. Call fetch_url on each of those 2 abstract URLs.\n"
        f"4. Call save_section_draft with section_key='{section_key}' "
        f"and exactly 2 items.\n\n"
        f"Each item must have:\n"
        f"- title: paper title verbatim from the page\n"
        f"- summary: 2 sentences, under 50 words total. "
        f"Sentence 1 = what they did. Sentence 2 = what they found.\n"
        f"- url: the arxiv.org/abs/<id> URL you fetched\n"
        f"- source: 'arXiv'\n\n"
        f"ABSOLUTE RULES:\n"
        f"- Maximum 3 fetch_url calls. No exceptions.\n"
        f"- If the first fetch returns 0 chars or an error, call fetch_url "
        f"ONCE on this fallback and pick 2 AI papers from it: "
        f"{fallback}\n"
        f"- NEVER guess or invent URLs. Only fetch URLs that appeared in "
        f"a page you already fetched, or the two URLs listed above.\n"
        f"- After save_section_draft, stop immediately."
    )
