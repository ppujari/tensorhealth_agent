"""
Agent loop.

Thin dispatcher:
  1. Send user prompt + tools to Groq
  2. Handle tool_calls (fetch_url, save_section_draft)
  3. Feed results back until the model says 'stop'

All section-specific logic lives in tools/<section>.py, not here.
"""

import json
from groq import Groq

from config import GROQ_API_KEY, MODEL, MAX_TOKENS, MAX_FETCHES_PER_RUN
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


def _handle_tool_calls(tool_calls, collected, fetch_count):
    """
    Process all tool calls from a Groq response.

    Returns (tool_result_messages, updated_fetch_count).
    """
    tool_result_messages = []
    for tc in tool_calls:
        name = tc.function.name
        args = json.loads(tc.function.arguments)

        if name == "fetch_url":
            url = args["url"]
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

        elif name == "save_section_draft":
            section_key = args["section_key"]
            items = args["items"]
            collected[section_key] = items
            print(f"  ✓ draft received for '{section_key}' ({len(items)} items)")
            result = {"status": "ok"}

        else:
            print(f"  ! unknown tool call: {name}")
            result = {"error": f"unknown tool: {name}"}

        tool_result_messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result),
        })

    return tool_result_messages, fetch_count


def run_research(user_prompt):
    """
    Run the agent loop for a single research prompt.

    Returns a dict: section_key -> list of items.
    """
    client = Groq(api_key=GROQ_API_KEY)
    tools = get_tools_for_run()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    collected = {}
    fetch_count = 0

    while True:
        print("→ calling Groq...")
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=tools,
        )

        choice = response.choices[0]
        message = choice.message

        if choice.finish_reason == "stop":
            print("← agent finished")
            return collected

        if choice.finish_reason == "tool_calls":
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })
            tool_results, fetch_count = _handle_tool_calls(
                message.tool_calls, collected, fetch_count
            )
            messages.extend(tool_results)
        else:
            print(f"! unexpected finish_reason: {choice.finish_reason}")
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
