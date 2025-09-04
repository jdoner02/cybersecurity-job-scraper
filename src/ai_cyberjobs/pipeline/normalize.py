from __future__ import annotations

import html
import re
from datetime import datetime
from typing import Any, Dict, List

from ..models import Job

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    txt = html.unescape(text)
    return _TAG_RE.sub(" ", txt).strip()


def _trim(text: str, limit: int = 600) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def map_usajobs_item(item: Dict[str, Any]) -> Job:
    # USAJOBS v1 Search API fields as commonly observed.
    # NOTE: Verify against latest API docs before production use.
    job_id = str(item.get("MatchedObjectId") or item.get("id") or "")
    pos = item.get("MatchedObjectDescriptor", {})
    title = pos.get("PositionTitle") or pos.get("Title") or ""
    org = pos.get("OrganizationName") or pos.get("DepartmentName") or ""
    locs: List[str] = [
        l.get("LocationName", "") for l in (pos.get("PositionLocation", []) or [])
    ]
    url = (
        pos.get("ApplyURI", [None])[0]
        or pos.get("PositionURI")
        or pos.get("ApplyURL")
        or "https://www.usajobs.gov"
    )
    summary = pos.get("UserArea", {}).get("Details", {}).get("JobSummary") or pos.get(
        "PositionSummary", ""
    )
    desc = _trim(_strip_html(summary or ""))
    posted_raw = pos.get("PublicationStartDate") or pos.get("PositionStartDate")
    posted_at: datetime
    try:
        posted_at = datetime.fromisoformat(str(posted_raw).replace("Z", "+00:00"))
    except Exception:
        posted_at = datetime.utcnow()

    salary = None
    grade = None
    try:
        salary = pos.get("UserArea", {}).get("Details", {}).get("LowGrade")
        if salary and pos.get("UserArea", {}).get("Details", {}).get("HighGrade"):
            salary = f"{salary}-{pos['UserArea']['Details']['HighGrade']}"
    except Exception:
        salary = None

    return Job(
        job_id=job_id,
        title=title,
        organization=org,
        locations=[l for l in locs if l] or ["Various"],
        description=desc,
        url=url,
        posted_at=posted_at,
        salary=salary,
        grade=grade,
        remote=None,
    )

