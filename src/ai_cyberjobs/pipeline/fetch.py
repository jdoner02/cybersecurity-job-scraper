from __future__ import annotations

from ..client.usajobs import USAJobsClient
from ..config import Category, Settings
from ..models import Job, Query
from ..queries import CATEGORIES


def fetch_category(settings: Settings, category: Category, *, days: int, limit: int) -> list[Job]:
    keywords = CATEGORIES[category]
    q = Query(category=category, keywords=keywords, days=days, limit=limit)
    client = USAJobsClient(settings)
    jobs: list[Job] = list(client.search(q))
    return jobs
