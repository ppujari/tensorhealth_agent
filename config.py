"""
Central configuration for the newsletter agent.

Supports multiple newsletter profiles. Each profile defines its
own sections, section order, ad placement, and sources.
"""

import os

# ---------- API ----------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "PLACEHOLDER_API_KEY")
MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 4096

# ---------- Output ----------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")

# ---------- Fetch behavior ----------
FETCH_DELAY_SECONDS = 1.5
MAX_PAGE_CHARS = 6000
MAX_FETCHES_PER_RUN = 4

# ---------- Styling ----------
BUTTON_STYLE = (
    "display:inline-block;"
    "padding:10px 20px;"
    "margin:8px 0 20px 0;"
    "background-color:#FF6719;"
    "color:#ffffff;"
    "text-decoration:none;"
    "border-radius:6px;"
    "font-family:sans-serif;"
    "font-weight:bold;"
)

# ---------- Ad templates ----------
# Self-promotion ads pointing to your Medium blog.
# Update these when you get a sponsor.

TENSORHEALTH_AD = """
<table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
  <tr>
    <td style="padding:20px;background:#f9f9f9;text-align:center;">
      <p style="margin:0 0 8px;font-family:sans-serif;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;">FROM THE AUTHOR</p>
      <p style="margin:0 0 12px;font-family:Georgia,serif;font-size:18px;font-weight:bold;color:#333;">Read more on Medical AI &amp; Deep Learning</p>
      <p style="margin:0 0 16px;font-family:sans-serif;font-size:14px;color:#555;">Explore in-depth articles on AI in healthcare, neural networks, and clinical applications.</p>
      <a href="https://ppujari.medium.com/" style="display:inline-block;padding:10px 24px;background-color:#FF6719;color:#ffffff;text-decoration:none;border-radius:6px;font-family:sans-serif;font-weight:bold;">Visit my Medium blog →</a>
    </td>
  </tr>
</table>
"""

AYNA_AD = """
<table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
  <tr>
    <td style="padding:20px;background:#f9f9f9;text-align:center;">
      <p style="margin:0 0 8px;font-family:sans-serif;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;">FROM THE AUTHOR</p>
      <p style="margin:0 0 12px;font-family:Georgia,serif;font-size:18px;font-weight:bold;color:#333;">Deep Dives on LLM Agents &amp; AI Architecture</p>
      <p style="margin:0 0 16px;font-family:sans-serif;font-size:14px;color:#555;">Technical articles on building agents, prompt engineering, and AI systems design.</p>
      <a href="https://ppujari.medium.com/" style="display:inline-block;padding:10px 24px;background-color:#FF6719;color:#ffffff;text-decoration:none;border-radius:6px;font-family:sans-serif;font-weight:bold;">Visit my Medium blog →</a>
    </td>
  </tr>
</table>
"""

# ---------- Newsletter Profiles ----------
# Each profile defines sections, order, and ad placement.

NEWSLETTERS = {
    "tensorhealth": {
        "name": "TensorHealth Newsletter",
        "subtitle": "Exploring the Intersection of AI and Healthcare Innovation",
        "section_order": [
            "th_opinion",
            "th_ai_shift",
            "th_news_bits",
            "th_holistic_health",
            # --- ad inserted here ---
            "th_events",
            "th_code_lab",
            "th_emerging_trends",
            "th_top_papers",
            "th_top_lectures",
        ],
        "ad_after_index": 3,  # after holistic_health (0-based)
        "ad_html": TENSORHEALTH_AD,
        "sections": {
            "th_opinion": {
                "title": "Opinion AI 🤖",
                "listing_urls": ["https://ppujari.medium.com/feed"],
                "lookback_days": 7,
            },
            "th_ai_shift": {
                "title": "AI-SHIFT 🌀",
                "listing_urls": [],
                "lookback_days": 7,
            },
            "th_news_bits": {
                "title": "News bits and bytes 🤩",
                "listing_urls": [],
                "lookback_days": 7,
            },
            "th_holistic_health": {
                "title": "❤️Holistic Health🌱",
                "listing_urls": [],
                "lookback_days": 7,
            },
            "th_events": {
                "title": "Upcoming Events 🗓️",
                "listing_urls": [],
                "lookback_days": 30,
            },
            "th_code_lab": {
                "title": "Clinical Code Lab: Step-by-Step Guides to AI💻",
                "listing_urls": [],
                "lookback_days": 14,
            },
            "th_emerging_trends": {
                "title": "Emerging Trends 📈",
                "listing_urls": [],
                "lookback_days": 7,
            },
            "th_top_papers": {
                "title": "Top Medical-AI Papers🧬",
                "listing_urls": [
                    "https://arxiv.org/a/rajpurkar_p_1",
                ],
                "fallback_url": "https://arxiv.org/list/cs.CV/recent",
                "lookback_days": 7,
            },
            "th_top_lectures": {
                "title": "Top Lectures🎓",
                "listing_urls": [],
                "lookback_days": 14,
            },
        },
    },

    "ayna": {
        "name": "Agents: All You Need — AYNA",
        "subtitle": "Your guide to the evolving world of LLMs and AI agents",
        "section_order": [
            "ayna_opinion",
            "ayna_ai_shift",
            "ayna_news_bits",
            "ayna_events",
            # --- ad inserted here ---
            "ayna_showcase",
            "ayna_emerging_trends",
            "ayna_dev_corner",
            "ayna_top_papers",
            "ayna_top_lectures",
        ],
        "ad_after_index": 3,  # after events (0-based)
        "ad_html": AYNA_AD,
        "sections": {
            "ayna_opinion": {
                "title": "Opinion AI ✍️",
                "listing_urls": ["https://ppujari.medium.com/feed"],
                "lookback_days": 7,
            },
            "ayna_ai_shift": {
                "title": "AI-SHIFT 🌀",
                "listing_urls": [
                    # To be populated — OpenAI blog, Anthropic news,
                    # Google DeepMind, Hugging Face blog
                ],
                "lookback_days": 7,
            },
            "ayna_news_bits": {
                "title": "News bits and bytes 🤩",
                "listing_urls": [
                    # To be populated — The Batch, Simon Willison,
                    # Lilian Weng, LangChain blog
                ],
                "lookback_days": 7,
            },
            "ayna_events": {
                "title": "Upcoming Events 📅",
                "listing_urls": [],
                "lookback_days": 30,
            },
            "ayna_showcase": {
                "title": "Agent Showcase 🚀",
                "listing_urls": [
                    # To be populated — GitHub trending, Product Hunt AI,
                    # agent framework releases
                ],
                "lookback_days": 14,
            },
            "ayna_emerging_trends": {
                "title": "Emerging Trends 🧭",
                "listing_urls": [],
                "lookback_days": 7,
            },
            "ayna_dev_corner": {
                "title": "Developers' Corner 🧑‍💻",
                "listing_urls": [
                    # To be populated — LangChain docs, CrewAI,
                    # AutoGen, Hugging Face tutorials
                ],
                "lookback_days": 14,
            },
            "ayna_top_papers": {
                "title": "Top AI Papers of the Week ⭐",
                "listing_urls": [
                    "https://arxiv.org/list/cs.AI/recent",
                ],
                "fallback_url": "https://arxiv.org/list/cs.CL/recent",
                "lookback_days": 7,
            },
            "ayna_top_lectures": {
                "title": "TOP LECTURES 🎓",
                "listing_urls": [],
                "lookback_days": 14,
            },
        },
    },
}


def get_newsletter(key):
    """Return a newsletter profile by key. Raises if not found."""
    if key not in NEWSLETTERS:
        available = ", ".join(NEWSLETTERS.keys())
        raise ValueError(f"Unknown newsletter '{key}'. Available: {available}")
    return NEWSLETTERS[key]
