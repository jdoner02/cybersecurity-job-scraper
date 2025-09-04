from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import cast

from pydantic import HttpUrl

from ai_cyberjobs.config import Settings, ensure_dirs
from ai_cyberjobs.models import Job
from ai_cyberjobs.pipeline.store import (
    sync_docs_data,
    write_history_snapshot,
    write_latest,
)


def make_settings(tmp_path: Path) -> Settings:
    s = Settings.model_construct(  # bypass env validation for tests
        usajobs_email="x@example.com",
        usajobs_api_key="k",
        repo_root=tmp_path,
        data_dir=tmp_path / "data",
        docs_data_dir=tmp_path / "docs" / "data",
        requests_timeout=20,
        rate_limit_per_min=10,
        default_days=2,
        results_limit=50,
    )
    ensure_dirs(s)
    return s


def test_write_and_sync(tmp_path: Path) -> None:
    s = make_settings(tmp_path)
    jobs = [
        Job(
            job_id="1",
            title="A",
            organization="Org",
            locations=["Here"],
            description="",
            url=cast(HttpUrl, "https://example.com/1"),
            posted_at=date(2024, 1, 1),
        ),
        Job(
            job_id="2",
            title="B",
            organization="Org",
            locations=["There"],
            description="",
            url=cast(HttpUrl, "https://example.com/2"),
            posted_at=date(2024, 1, 2),
        ),
    ]
    lp = write_latest(s, "ai", jobs)
    assert lp.exists()
    data = json.loads(lp.read_text())
    assert isinstance(data, list) and len(data) == 2
    hp = write_history_snapshot(s, "ai", jobs)
    assert hp.exists()
    dp = sync_docs_data(s, "ai")
    assert dp.exists()
    docs = json.loads(dp.read_text())
    assert len(docs) == 2
