"""
Agent loop.

Thin dispatcher:
  1. Send user prompt + tools to Claude
  2. Handle tool_use blocks (fetch_url, save_section_draft)
  3. Feed results back until Claude says 'end_turn'

All section-specific logic lives in tools/<section>.py, not here.
"""

import json
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS, MAX_FETCHES_PER_RUN
from tools.schemas import get_tools_for_run
from tools.fetcher import fetch_url
from rendering.html_builder import render_document
from storage.drafts import save_draft


SYSTEM_PROMPT = (
    "You are the TensorHealth newsletter research agent. Your job is to "
    "research and draft sections of a weekly medical-AI newsletter.\n\n"
    "Rules:\n"
    "- Use the fetch_url tool to read curated listing pages, then follow "
    "links to individual papers/articles.\n"
    "- Never invent facts, findings, titles, or URLs. Every claim must "
    "come from a page you actually fetched.\n"
    "- If a fetch returns an error, try a different URL from the listings "
    "rather than guessing content.\n"
    "- Write summaries in plain English. Avoid hype.\n"
    "- When finished researching a section, call save_section_draft "
    "exactly once with the curated items.\n"
    "- Stay within the fetch budget — don't fetch the same URL twice."
)


def _handle_tool_calls(response_content, collected, fetch_count):
    """
    Process all tool_use blocks in a response.

    Returns (tool_result_blocks, updated_fetch_count).
    """
    tool_results = []
    for block in response_content:
        if block.type != "tool_use":
            continue

        if block.name == "fetch_url":
            url = block.input["url"]
            if fetch_count >= MAX_FETCHES_PER_RUN:
                result = {
                    "status": "error",
                    "url": url,
                    "text": "",
                    "error": f"fetch budget exceeded ({MAX_FETCHES_PER_RUN} fetches)",
                }
                print(f"  ! fetch budget exceeded, denying: {url}")
            else:
                print(f"  → fetch_url: {url}")
                result = fetch_url(url)
                fetch_count += 1
                if result["status"] == "ok":
                    print(f"    ✓ got {len(result['text'])} chars")
                else:
                    print(f"    ! {result['error']}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

        elif block.name == "save_section_draft":
            section_key = block.input["section_key"]
            items = block.input["items"]
            collected[section_key] = items
            print(f"  ✓ draft received for '{section_key}' ({len(items)} items)")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps({"status": "ok"}),
            })

        else:
            print(f"  ! unknown tool call: {block.name}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps({"error": f"unknown tool: {block.name}"}),
                "is_error": True,
            })

    return tool_results, fetch_count


def run_research(user_prompt):
    """
    Run the agent loop for a single research prompt.

    Returns a dict: section_key -> list of items.
    """
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    tools = get_tools_for_run()
    messages = [{"role": "user", "content": user_prompt}]
    collected = {}
    fetch_count = 0

    while True:
        print("→ calling Claude...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            print("← agent finished")
            return collected

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results, fetch_count = _handle_tool_calls(
                response.content, collected, fetch_count
            )
            messages.append({"role": "user", "content": tool_results})
        else:
            print(f"! unexpected stop_reason: {response.stop_reason}")
            return collected


def build_and_save(newsletter_title, collected, newsletter):
    """Turn collected section data into HTML and save to disk."""
    if not collected:
        print("! no sections were drafted — nothing to save")
        return None

    html = render_document(newsletter_title, collected, newsletter)
    section_key = list(collected.keys())[0] if len(collected) == 1 else None
    path = save_draft(html, section_key=section_key)
    print(f"✓ draft saved to: {path}")
    return path
