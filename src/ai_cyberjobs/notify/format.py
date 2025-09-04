from __future__ import annotations

from typing import Iterable, Tuple

from ..models import Job


def make_subject(category: str, count: int) -> str:
    prefix = "AI" if category == "ai" else "Cybersecurity"
    return f"New {prefix} Jobs ({count}) – USAJOBS"


def render_email_bodies(category: str, jobs: Iterable[Job]) -> Tuple[str, str]:
    items = list(jobs)
    html_items = []
    text_items = []
    for j in items:
        html_items.append(
            f"<li><strong>{escape(j.job_id)}</strong>: {escape(j.description)} <a href='{j.url}'>Apply</a></li>"
        )
        text_items.append(f"- {j.job_id}: {j.description}\n  {j.url}")

    html = """
<!doctype html>
<html><body>
  <p>New postings found on USAJOBS:</p>
  <ul>
    {items}
  </ul>
</body></html>
""".strip().format(items="\n    ".join(html_items))

    text = "New postings found on USAJOBS:\n\n" + "\n\n".join(text_items)
    return html, text


def escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
    )

