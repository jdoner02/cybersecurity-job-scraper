from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from ..config import Settings
from ..models import Job


def to_dict(j: Job) -> dict:
    d = j.model_dump()
    # Coerce posted_at to isoformat string for consistent JSON
    pa = d.get("posted_at")
    if hasattr(pa, "isoformat"):
        d["posted_at"] = pa.isoformat()
    return d


def write_latest(settings: Settings, category: str, jobs: List[Job]) -> Path:
    latest_path = settings.data_dir / "latest" / f"{category}_jobs.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    # sort by posted_at desc then job_id for determinism
    jobs_sorted = sorted(
        jobs,
        key=lambda j: (str(getattr(j.posted_at, "isoformat", lambda: j.posted_at)()), j.job_id),
        reverse=True,
    )
    with latest_path.open("w", encoding="utf-8") as f:
        json.dump([to_dict(j) for j in jobs_sorted], f, indent=2)
    # also write CSV
    write_csv(settings, category, jobs_sorted)
    return latest_path


def write_csv(settings: Settings, category: str, jobs: List[Job]) -> Path:
    csv_path = settings.data_dir / "latest" / f"{category}_jobs.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "title", "organization", "locations", "url", "posted_at"])
        for j in jobs:
            w.writerow([j.job_id, j.title, j.organization, ", ".join(j.locations), str(j.url), getattr(j.posted_at, "isoformat", lambda: j.posted_at)()])
    return csv_path


def write_history_snapshot(settings: Settings, category: str, jobs: List[Job]) -> Path:
    date_str = datetime.utcnow().date().isoformat()
    hist_path = settings.data_dir / "history" / category / f"{date_str}.json"
    if not hist_path.exists():
        hist_path.parent.mkdir(parents=True, exist_ok=True)
        with hist_path.open("w", encoding="utf-8") as f:
            json.dump([to_dict(j) for j in jobs], f, indent=2)
    return hist_path


def write_new_jobs(settings: Settings, category: str, new_jobs: List[Job]) -> Path:
    path = settings.data_dir / "latest" / f"new_{category}_jobs.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump([to_dict(j) for j in new_jobs], f, indent=2)
    return path


def sync_docs_data(settings: Settings, category: str) -> Path:
    src = settings.data_dir / "latest" / f"{category}_jobs.json"
    dst = settings.docs_data_dir / f"{category}_jobs.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        dst.write_bytes(src.read_bytes())
    else:
        dst.write_text("[]", encoding="utf-8")
    return dst

