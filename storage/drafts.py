"""
Draft storage.

Writes generated HTML to disk. Kept in its own module so we can
later swap local-disk saving for Google Drive, email delivery,
S3, etc. without touching the rendering or agent code.
"""

import os
from datetime import datetime
from config import DRAFTS_DIR


def save_draft(html, section_key=None):
    """
    Write an HTML draft to disk and return its path.

    Filename includes today's date and (optionally) the section key
    so successive runs don't overwrite each other.
    """
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    suffix = f"_{section_key}" if section_key else ""
    filename = f"tensorhealth_{date}{suffix}.html"
    path = os.path.join(DRAFTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
