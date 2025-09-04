from __future__ import annotations

from typing import Iterable, List

from ..config import Category, Settings
from ..models import Job, Query
from ..queries import CATEGORIES
from ..client.usajobs import USAJobsClient


def fetch_category(settings: Settings, category: Category, *, days: int, limit: int) -> List[Job]:
    keywords = CATEGORIES[category]
    q = Query(category=category, keywords=keywords, days=days, limit=limit)
    client = USAJobsClient(settings)
    jobs: List[Job] = list(client.search(q))
    return jobs

