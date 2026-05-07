"""
HTML builder.

Renders all section headings for a given newsletter profile.
Injects the ad block at the configured position. Sections with
data get content + buttons; sections without get placeholders.
"""

from html import escape
from config import BUTTON_STYLE
from rendering.template import PLACEHOLDER_TEXT


def _button(url):
    safe_url = escape(url, quote=True)
    return f'<p><a href="{safe_url}" style="{BUTTON_STYLE}">Read more</a></p>'


def _item_html(item):
    title = escape(item["title"])
    summary = escape(item["summary"])
    source = escape(item.get("source", ""))
    source_tag = f" <em>({source})</em>" if source else ""
    return (
        f'<p><strong>{title}</strong>{source_tag}</p>\n'
        f'<p>{summary}</p>\n'
        f'{_button(item["url"])}'
    )


def _placeholder():
    return f'<p style="color:#999;font-style:italic;">{PLACEHOLDER_TEXT}</p>'


def render_document(title, collected, newsletter):
    """
    Render the full newsletter HTML.

    Args:
        title:       newsletter title (<h1>)
        collected:   dict of section_key -> list of items
        newsletter:  newsletter profile dict from config

    Returns:
        Full HTML document string.
    """
    section_order = newsletter["section_order"]
    sections = newsletter["sections"]
    ad_after = newsletter.get("ad_after_index")
    ad_html = newsletter.get("ad_html", "")

    body_parts = [f"<h1>{escape(title)}</h1>"]

    for i, section_key in enumerate(section_order):
        heading = escape(sections[section_key]["title"])
        body_parts.append(f"<h2>{heading}</h2>")

        items = collected.get(section_key)
        if items:
            body_parts.extend(_item_html(item) for item in items)
        else:
            body_parts.append(_placeholder())

        # Inject ad after the configured section
        if ad_after is not None and i == ad_after and ad_html:
            body_parts.append(ad_html)

    body = "\n\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 680px; margin: 2em auto;
          padding: 0 1em; line-height: 1.6; }}
  h1 {{ font-size: 2em; }}
  h2 {{ font-size: 1.4em; margin-top: 1.5em; }}
  em {{ color: #555; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""
