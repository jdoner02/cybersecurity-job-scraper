from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from ..config import Settings
from ..models import Job


def _state_path(settings: Settings, category: str) -> Path:
    return settings.data_dir / "state" / f"known_{category}_ids.json"


def load_known_ids(settings: Settings, category: str) -> set[str]:
    path = _state_path(settings, category)
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {str(x) for x in data}
    except Exception:
        return set()


def save_known_ids(settings: Settings, category: str, ids: set[str]) -> None:
    path = _state_path(settings, category)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(sorted(ids), f, indent=2)


def compute_new_jobs(
    settings: Settings, category: str, jobs: Iterable[Job]
) -> tuple[list[Job], set[str]]:
    existing = load_known_ids(settings, category)
    new_jobs: list[Job] = []
    all_ids: set[str] = set(existing)
    for j in jobs:
        if j.job_id not in existing:
            new_jobs.append(j)
        all_ids.add(j.job_id)
    return new_jobs, all_ids
