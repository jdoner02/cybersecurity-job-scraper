from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field, HttpUrl


class Job(BaseModel):
    job_id: str
    title: str
    organization: str
    locations: list[str]
    description: str = Field(default="")
    url: HttpUrl
    posted_at: date | datetime
    salary: str | None = None
    grade: str | None = None
    remote: bool | None = None


class Query(BaseModel):
    category: str
    keywords: list[str]
    days: int = 2
    limit: int = 50


class ResultSet(BaseModel):
    category: str
    jobs: list[Job]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
