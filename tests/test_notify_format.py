from __future__ import annotations

from datetime import date
from typing import cast

from pydantic import HttpUrl

from ai_cyberjobs.models import Job
from ai_cyberjobs.notify.format import make_subject, render_email_bodies


def test_email_formatting() -> None:
    jobs = [
        Job(
            job_id="123",
            title="Sec Analyst",
            organization="X",
            locations=["Remote"],
            description="Investigate alerts.",
            url=cast(HttpUrl, "https://example.com/j/123"),
            posted_at=date(2024, 1, 1),
        )
    ]
    html, text = render_email_bodies("cyber", jobs)
    assert "123" in html and "Apply" in html
    assert "123" in text and "https://example.com/j/123" in text
    subj = make_subject("cyber", 1)
    assert subj.startswith("New Cybersecurity Jobs")
