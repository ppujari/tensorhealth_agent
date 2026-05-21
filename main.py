"""
TensorHealth / AYNA newsletter agent — entry point.

Usage:
    python main.py                 # interactive menu
    python main.py tensorhealth    # run TensorHealth directly
    python main.py ayna            # run AYNA directly
"""

import sys
from datetime import datetime

from config import get_newsletter
from agent import run_research, build_and_save
from tools import opinion, papers, ai_shift, showcase, news, dev_corner, trends, events, hiring


def run(newsletter_key):
    newsletter = get_newsletter(newsletter_key)
    print("=" * 60)
    print(f"Newsletter Agent — {newsletter['name']}")
    print("=" * 60)

    all_collected = {}

    # --- Section: Opinion ---
    opinion_key = [k for k in newsletter["section_order"] if "opinion" in k][0]
    print(f"\n--- {newsletter['sections'][opinion_key]['title']} ---")
    prompt = opinion.build_research_prompt(section_key=opinion_key)
    collected = run_research(prompt)
    all_collected.update(collected)

    # --- Section: AI-SHIFT (local PDF) ---
    shift_key = [k for k in newsletter["section_order"] if "shift" in k][0]
    print(f"\n--- {newsletter['sections'][shift_key]['title']} ---")
    prompt = ai_shift.build_research_prompt(section_key=shift_key)
    if prompt:  # None if no PDF found
        collected = run_research(prompt)
        all_collected.update(collected)

    # --- Section: News bits and bytes (RSS feeds) ---
    news_key = [k for k in newsletter["section_order"] if "news" in k][0]
    print(f"\n--- {newsletter['sections'][news_key]['title']} ---")
    prompt = news.build_research_prompt(section_key=news_key)
    if prompt:
        collected = run_research(prompt)
        all_collected.update(collected)

    # --- Section: Agent Showcase (AYNA only) ---
    showcase_keys = [k for k in newsletter["section_order"] if "showcase" in k]
    if showcase_keys:
        sc_key = showcase_keys[0]
        print(f"\n--- {newsletter['sections'][sc_key]['title']} ---")
        prompt = showcase.build_research_prompt(section_key=sc_key)
        collected = run_research(prompt)
        all_collected.update(collected)

    # --- Section: Developers' Corner / Clinical Code Lab ---
    dev_keys = [k for k in newsletter["section_order"]
                if "dev_corner" in k or "code_lab" in k]
    if dev_keys:
        dev_key = dev_keys[0]
        print(f"\n--- {newsletter['sections'][dev_key]['title']} ---")
        prompt = dev_corner.build_research_prompt(section_key=dev_key)
        if prompt:
            collected = run_research(prompt)
            all_collected.update(collected)

    # --- Section: Top Papers ---
    papers_key = [k for k in newsletter["section_order"] if "papers" in k][0]
    papers_cfg = newsletter["sections"][papers_key]
    print(f"\n--- {papers_cfg['title']} ---")
    listing_url = papers_cfg["listing_urls"][0] if papers_cfg["listing_urls"] else None
    fallback_url = papers_cfg.get("fallback_url")
    prompt = papers.build_research_prompt(
        section_key=papers_key,
        listing_url=listing_url,
        fallback_url=fallback_url,
    )
    collected = run_research(prompt)
    all_collected.update(collected)

    # --- Section: Upcoming Events ---
    events_key = [k for k in newsletter["section_order"] if "events" in k][0]
    print(f"\n--- {newsletter['sections'][events_key]['title']} ---")
    prompt = events.build_research_prompt(section_key=events_key)
    collected = run_research(prompt) 
    all_collected.update(collected)

    # --- Section: Top AI Hiring ---
    hiring_keys = [k for k in newsletter["section_order"] if "hiring" in k]
    if hiring_keys:
        hiring_key = hiring_keys[0]
        hiring_cfg = newsletter["sections"][hiring_key]
        print(f"\n--- {hiring_cfg['title']} ---")
        listing_url = hiring_cfg["listing_urls"][0] if hiring_cfg["listing_urls"] else None
        prompt = hiring.build_research_prompt(
            section_key=hiring_key,
            listing_url=listing_url,
        )
        collected = run_research(prompt)
        all_collected.update(collected)


    # --- Section: Emerging Trends (runs LAST — synthesizes from above) ---
    trends_key = [k for k in newsletter["section_order"] if "trends" in k][0]
    print(f"\n--- {newsletter['sections'][trends_key]['title']} ---")
    prompt = trends.build_research_prompt(
        section_key=trends_key,
        already_collected=all_collected,
    )
    if prompt:
        collected = run_research(prompt)
        all_collected.update(collected)

    # --- Render all sections (populated + placeholders + ad) ---
    date = datetime.now().strftime("%B %d, %Y")
    title = f"{newsletter['name']} — {date}"
    build_and_save(title, all_collected, newsletter)

    print("\nDone. Open the HTML file in your browser, Ctrl+A to select all,")
    print("Ctrl+C to copy, then paste into Substack.")


def main():
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        print("Which newsletter do you want to generate?\n")
        print("  1. tensorhealth  — TensorHealth Newsletter")
        print("  2. ayna          — Agents: All You Need")
        print()
        choice = input("Enter 1 or 2 (or name): ").strip()
        key_map = {"1": "tensorhealth", "2": "ayna"}
        key = key_map.get(choice, choice)
        run(key)


if __name__ == "__main__":
    main()
