from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field


class Job(BaseModel):
    job_id: str
    title: str
    organization: str
    locations: List[str]
    description: str = Field(default="")
    url: HttpUrl
    posted_at: date | datetime
    salary: Optional[str] = None
    grade: Optional[str] = None
    remote: Optional[bool] = None


class Query(BaseModel):
    category: str
    keywords: List[str]
    days: int = 2
    limit: int = 50


class ResultSet(BaseModel):
    category: str
    jobs: List[Job]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

