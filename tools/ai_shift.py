"""
AI-SHIFT section.

Source: article.pdf in inputs/ai_shift/ (clipped from FT Monday paper).
Link:   link.txt in the same folder (one URL per line, first line used).

Works for both newsletters:
  TensorHealth: section_key='th_ai_shift'
  AYNA:         section_key='ayna_ai_shift'
"""

import os
import base64
import glob
import fitz  # PyMuPDF
from pypdf import PdfReader
from config import PROJECT_ROOT

INPUT_DIR = os.path.join(PROJECT_ROOT, "inputs", "ai_shift")


def _find_latest_pdf():
    os.makedirs(INPUT_DIR, exist_ok=True)
    pdfs = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))
    if not pdfs:
        return None
    return max(pdfs, key=os.path.getmtime)


def _read_link():
    """Read the article URL from link.txt. Falls back to ft.com."""
    link_file = os.path.join(INPUT_DIR, "link.txt")
    if os.path.exists(link_file):
        with open(link_file, "r", encoding="utf-8") as f:
            url = f.readline().strip()
            if url:
                return url
    return "https://www.ft.com"


def _extract_text(pdf_path, max_chars=6000):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[...truncated...]"
            break
    return text.strip()


def _pages_to_images(pdf_path, max_pages=3, dpi=150):
    doc = fitz.open(pdf_path)
    images = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        png_bytes = pix.tobytes("png")
        b64 = base64.standard_b64encode(png_bytes).decode("utf-8")
        images.append(b64)
    doc.close()
    return images


def _build_text_prompt(text, section_key, url):
    return (
        f"Summarize the following newspaper article for the AI-SHIFT "
        f"section of a newsletter.\n\n"
        f"--- ARTICLE TEXT ---\n"
        f"{text}\n"
        f"--- END ---\n\n"
        f"Call save_section_draft with section_key='{section_key}' "
        f"and exactly 1 item.\n\n"
        f"The item must have:\n"
        f"- title: a clear headline summarizing the article's main point\n"
        f"- summary: 3-4 sentence summary of the key shift or development. "
        f"Focus on what changed and why it matters. Under 80 words.\n"
        f"- url: '{url}'\n"
        f"- source: 'Financial Times'\n\n"
        f"RULES:\n"
        f"- Do NOT call fetch_url. All content is above.\n"
        f"- Summarize only what is in the article.\n"
        f"- After save_section_draft, stop immediately."
    )


def _build_image_prompt(images, section_key, url):
    content = []
    content.append({
        "type": "text",
        "text": (
            f"The following images are pages from a newspaper article. "
            f"Read the text from the images and summarize the article for "
            f"the AI-SHIFT section of a newsletter.\n\n"
            f"Call save_section_draft with section_key='{section_key}' "
            f"and exactly 1 item.\n\n"
            f"The item must have:\n"
            f"- title: a clear headline summarizing the article's main point\n"
            f"- summary: 3-4 sentence summary of the key shift or development. "
            f"Focus on what changed and why it matters. Under 80 words.\n"
            f"- url: '{url}'\n"
            f"- source: 'Financial Times'\n\n"
            f"RULES:\n"
            f"- Do NOT call fetch_url.\n"
            f"- Summarize only what you can read from the images.\n"
            f"- After save_section_draft, stop immediately."
        ),
    })
    for b64 in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": b64,
            },
        })
    return content


def build_research_prompt(section_key="th_ai_shift"):
    pdf_path = _find_latest_pdf()
    if not pdf_path:
        print(f"  ! no PDF found in {INPUT_DIR} — skipping AI-SHIFT")
        return None

    filename = os.path.basename(pdf_path)
    url = _read_link()
    print(f"  reading PDF: {filename}")
    print(f"  link: {url}")

    # Try text extraction first
    text = _extract_text(pdf_path)
    if len(text.strip()) >= 100:
        print(f"  ✓ extracted {len(text)} chars of text")
        return _build_text_prompt(text, section_key, url)

    # Scanned PDF — use Claude's vision
    print(f"  text extraction got {len(text)} chars — using vision instead")
    images = _pages_to_images(pdf_path)
    if not images:
        print(f"  ! could not convert PDF pages to images")
        return None

    print(f"  ✓ converted {len(images)} page(s) to images for vision")
    return _build_image_prompt(images, section_key, url)