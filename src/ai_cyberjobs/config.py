from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Root = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Root / ".env"), env_prefix="", case_sensitive=False
    )

    # USAJOBS API credentials (required for real runs)
    # Accept either standard envs or hyphenated keys found in some setups
    usajobs_email: str = Field(
        default="",
        validation_alias=AliasChoices("USAJOBS_EMAIL", "usajobs-api-email"),
    )
    usajobs_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("USAJOBS_API_KEY", "usajobs-api-key"),
    )

    # Tuning
    requests_timeout: int = Field(20, alias="REQUESTS_TIMEOUT")
    rate_limit_per_min: int = Field(10, alias="RATE_LIMIT_PER_MIN")
    default_days: int = Field(2, alias="DEFAULT_DAYS")
    results_limit: int = Field(50, alias="RESULTS_LIMIT")

    # Paths
    repo_root: Path = Root
    data_dir: Path = Root / "data"
    docs_data_dir: Path = Root / "docs" / "data"


Category = Literal["ai", "cyber"]


def ensure_dirs(settings: Settings) -> None:
    for p in [
        settings.data_dir / "state",
        settings.data_dir / "history" / "ai",
        settings.data_dir / "history" / "cyber",
        settings.data_dir / "latest",
        settings.docs_data_dir,
        settings.repo_root / "out" / "emails",
    ]:
        p.mkdir(parents=True, exist_ok=True)
