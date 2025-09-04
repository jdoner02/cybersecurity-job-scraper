from __future__ import annotations

from ai_cyberjobs.models import Job
from ai_cyberjobs.notify.format import make_subject, render_email_bodies


def test_email_formatting():
    jobs = [
        Job(job_id="123", title="Sec Analyst", organization="X", locations=["Remote"], description="Investigate alerts.", url="https://example.com/j/123", posted_at="2024-01-01")
    ]
    html, text = render_email_bodies("cyber", jobs)
    assert "123" in html and "Apply" in html
    assert "123" in text and "https://x" in text
    subj = make_subject("cyber", 1)
    assert subj.startswith("New Cybersecurity Jobs")
