from __future__ import annotations

from ..client.usajobs import USAJobsClient
from ..config import Category, Settings
from ..models import Job, Query
from ..queries import CATEGORIES


def fetch_category(settings: Settings, category: Category, *, days: int, limit: int) -> list[Job]:
    """Fetch jobs for a category.

    If required credentials are missing (common in a local environment before
    the user configures a .env) we return an empty list instead of failing so
    that commands like `validate` or a dry-run scrape remain usable.
    """
    if not settings.usajobs_email or not settings.usajobs_api_key:
        # Soft fail: allow local dev without secrets
        return []
    keywords = CATEGORIES[category]
    q = Query(category=category, keywords=keywords, days=days, limit=limit)
    client = USAJobsClient(settings)
    jobs: list[Job] = list(client.search(q))
    return jobs
