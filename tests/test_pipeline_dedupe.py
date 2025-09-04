from __future__ import annotations

from pathlib import Path

from ai_cyberjobs.config import Settings, ensure_dirs
from ai_cyberjobs.models import Job
from ai_cyberjobs.pipeline.dedupe import compute_new_jobs, save_known_ids


def make_settings(tmp_path: Path) -> Settings:
    # Create a temporary settings by constructing directly (no env)
    s = Settings.model_construct(
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


def test_compute_new_jobs(tmp_path: Path) -> None:
    s = make_settings(tmp_path)
    old_ids = {"a", "b"}
    save_known_ids(s, "ai", old_ids)
    jobs = [
        Job(
            job_id="a",
            title="t",
            organization="o",
            locations=["L"],
            description="",
            url="https://example.com/a",
            posted_at="2024-01-01",
        ),
        Job(
            job_id="c",
            title="t2",
            organization="o2",
            locations=["L"],
            description="",
            url="https://example.com/c",
            posted_at="2024-01-01",
        ),
    ]
    new_jobs, all_ids = compute_new_jobs(s, "ai", jobs)
    assert [j.job_id for j in new_jobs] == ["c"]
    assert all_ids == {"a", "b", "c"}
