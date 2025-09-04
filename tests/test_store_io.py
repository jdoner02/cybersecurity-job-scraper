from __future__ import annotations

import json
from pathlib import Path

from ai_cyberjobs.config import Settings, ensure_dirs
from ai_cyberjobs.models import Job
from ai_cyberjobs.pipeline.store import write_latest, write_history_snapshot, sync_docs_data


def make_settings(tmp_path: Path) -> Settings:
    s = Settings(USAJOBS_EMAIL="x@example.com", USAJOBS_API_KEY="k")
    s.repo_root = tmp_path
    s.data_dir = tmp_path / "data"
    s.docs_data_dir = tmp_path / "docs" / "data"
    ensure_dirs(s)
    return s


def test_write_and_sync(tmp_path: Path):
    s = make_settings(tmp_path)
    jobs = [
        Job(job_id="1", title="A", organization="Org", locations=["Here"], description="", url="https://x", posted_at="2024-01-01"),
        Job(job_id="2", title="B", organization="Org", locations=["There"], description="", url="https://x", posted_at="2024-01-02"),
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

