# TensorHealth Newsletter Agent

Agentic LLM workflow for drafting the weekly TensorHealth medical-AI newsletter.
Runs locally on Windows/Mac/Linux. Outputs an HTML file ready to paste into
the Substack editor.

## Status

**v1** implements the **Top Medical-AI Papers** section only. Additional
sections will be added one per development week following the build plan
(see project notes).

## Project Layout

```
tensorhealth-agent/
├── main.py              # Entry point
├── agent.py             # Thin agent loop + tool dispatch
├── config.py            # API key, model, sources, styling
├── requirements.txt
├── tools/
│   ├── schemas.py       # Tool schemas (web_search + save_section_draft)
│   └── papers.py        # Section 8: research prompt builder
├── rendering/
│   ├── template.py      # 9-section order
│   └── html_builder.py  # HTML rendering + inline-styled buttons
├── storage/
│   └── drafts.py        # Save HTML drafts to disk
└── drafts/              # Generated HTML files land here (created on first run)
```

## Design Principles

- **One section = one file under `tools/`.** Adding a section never
  touches existing section code.
- **Rendering is decoupled from research.** `rendering/` takes data,
  not prompts or API responses.
- **Storage is isolated.** Swap local disk for Drive/email later
  without touching anything else.
- **Inline CSS for buttons.** Survives the Substack copy-paste.
- **No invented facts.** The system prompt forbids it; every claim
  must come from a web_search result.

## Setup

```powershell
# From the project folder
python -m venv agent-venv
.\agent-venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set your API key (or edit config.py)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

## Run

```powershell
python main.py
```

The agent will:
1. Search the web for medical-AI papers from the past 7 days
2. Pick the top 2-3
3. Summarize each in plain English
4. Save an HTML file to `drafts/tensorhealth_YYYY-MM-DD_top_papers.html`

Open the HTML file in your browser, select all, copy, and paste into
Substack under your `## Top Medical-AI Papers🧬` heading.

## Adding a New Section (for future development weeks)

1. Create `tools/<section_name>.py` with a `build_research_prompt()` function
2. Add the section config to `SECTIONS` in `config.py` (if not already there)
3. Import and call it from `main.py`

No changes to `agent.py`, `rendering/`, or `storage/` needed.
