from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import Settings
from ..models import Job, Query
from ..pipeline.normalize import map_usajobs_item


@dataclass
class _Throttle:
    per_min: int
    _last_ts: float = 0.0

    def sleep_if_needed(self) -> None:
        if self.per_min <= 0:
            return
        min_interval = 60.0 / float(self.per_min)
        now = time.time()
        delta = now - self._last_ts
        if delta < min_interval:
            time.sleep(min_interval - delta)
        self._last_ts = time.time()


class USAJobsClient:
    """
    USAJOBS Search API client.

    Auth headers are typically:
      - User-Agent: the registered email
      - Authorization-Key: the API key

    NOTE: Please re-verify header names and endpoints against the latest
    official documentation before production deployment.
    """

    BASE_URL = "https://data.usajobs.gov/api/search"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": settings.usajobs_email,
                "Authorization-Key": settings.usajobs_api_key,
                "Accept": "application/json",
            }
        )
        self._throttle = _Throttle(settings.rate_limit_per_min)

    def search(self, query: Query) -> Iterator[Job]:
        keyword = build_keyword_query(query.keywords)
        limit = max(1, query.limit)
        page = 1
        fetched = 0
        while fetched < limit:
            remaining = limit - fetched
            page_size = min(50, remaining)
            data = self._search_page(keyword=keyword, days=query.days, page=page, size=page_size)
            items = data.get("SearchResult", {}).get("SearchResultItems", [])
            if not items:
                break
            for raw in items:
                # Common envelope: {"MatchedObjectId": ..., "MatchedObjectDescriptor": {...}}
                job = map_usajobs_item(raw)
                yield job
                fetched += 1
                if fetched >= limit:
                    break
            page += 1

    @retry(
        retry=retry_if_exception_type((requests.RequestException,)),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _search_page(self, *, keyword: str, days: int, page: int, size: int) -> dict[str, Any]:
        self._throttle.sleep_if_needed()
        params: dict[str, str] = {
            "Keyword": keyword,
            # DatePosted: 1 (24h), 3, 7, 30 etc. Using days ceiling mapping.
            "DatePosted": str(normalize_days(days)),
            "ResultsPerPage": str(size),
            "Page": str(page),
        }
        resp = self.session.get(
            self.BASE_URL, params=params, timeout=self.settings.requests_timeout
        )
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())


def build_keyword_query(keywords: list[str]) -> str:
    """Return a keyword string for USAJOBS.

    Observed behavior (empirical): using an "A OR B OR C" style query can
    sometimes yield zero results even when individual primary terms return
    matches. To reduce over-filtering we bias toward the *first* high-signal
    phrase when more than ~4 keywords are supplied. This keeps the search
    broad (logical implicit OR / relevance weighting server side) and avoids
    accidental exclusion.

    Strategy:
    - If <=4 keywords: join with spaces (space-delimited behaves like broad search)
    - If >4 keywords: use only the first phrase (usually "artificial intelligence" for AI)
    - Terms with spaces are kept quoted for safety.
    """
    kws = [k.strip() for k in keywords if k.strip()]
    if not kws:
        return ""
    if len(kws) > 4:
        primary = kws[0]
        return f'"{primary}"' if " " in primary else primary
    # Broad multi-term: space joined
    def render(t: str) -> str:
        return f'"{t}"' if " " in t else t
    return " ".join(render(k) for k in kws)


def normalize_days(days: int) -> int:
    # Map arbitrary day window to a supported DatePosted bucket.
    if days <= 1:
        return 1
    if days <= 3:
        return 3
    if days <= 7:
        return 7
    return 30
