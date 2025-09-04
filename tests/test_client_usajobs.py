from __future__ import annotations

from ai_cyberjobs.pipeline.normalize import map_usajobs_item


def test_map_usajobs_item_minimal():
    sample = {
        "MatchedObjectId": "12345",
        "MatchedObjectDescriptor": {
            "PositionTitle": "AI Researcher",
            "OrganizationName": "Test Agency",
            "PositionLocation": [{"LocationName": "Remote"}],
            "UserArea": {"Details": {"JobSummary": "<p>Lead AI research on mission-critical systems.</p>"}},
            "ApplyURI": ["https://example.com/apply"],
            "PublicationStartDate": "2024-01-01T00:00:00Z",
        },
    }

    job = map_usajobs_item(sample)
    assert job.job_id == "12345"
    assert job.title == "AI Researcher"
    assert job.organization == "Test Agency"
    assert job.locations == ["Remote"]
    assert job.url == "https://example.com/apply"
    assert "Lead AI research" in job.description

