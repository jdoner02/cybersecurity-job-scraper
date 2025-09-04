from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .config import Settings, ensure_dirs
from .models import Job
from .pipeline.dedupe import compute_new_jobs, save_known_ids
from .pipeline.fetch import fetch_category
from .pipeline.store import (
    sync_docs_data,
    write_history_snapshot,
    write_latest,
    write_new_jobs,
)
from .notify.format import make_subject, render_email_bodies


app = typer.Typer(add_completion=False, help="AI & Cybersecurity USAJOBS scraper")


@app.command()
def scrape(
    category: str = typer.Option("both", help="ai|cyber|both"),
    days: int = typer.Option(None, help="Lookback days window"),
    limit: int = typer.Option(None, help="Max results to fetch per category"),
    dry_run: bool = typer.Option(False, help="Do not write outputs/state"),
):
    """Fetch jobs for a category and update data/state/history.

    If dry-run, prints a summary and writes nothing.
    """
    settings = Settings()
    ensure_dirs(settings)
    days = days or settings.default_days
    limit = limit or settings.results_limit

    cats = ["ai", "cyber"] if category == "both" else [category]
    summary: dict[str, int] = {}
    for c in cats:
        jobs = fetch_category(settings, c, days=days, limit=limit)
        new_jobs, all_ids = compute_new_jobs(settings, c, jobs)
        summary[c] = len(new_jobs)
        if dry_run:
            typer.secho(f"[dry-run] {c}: {len(jobs)} jobs, {len(new_jobs)} new", fg=typer.colors.YELLOW)
            continue
        write_latest(settings, c, jobs)
        write_history_snapshot(settings, c, jobs)
        write_new_jobs(settings, c, new_jobs)
        save_known_ids(settings, c, all_ids)
        sync_docs_data(settings, c)
        typer.echo(f"{c}: {len(jobs)} jobs, {len(new_jobs)} new")

    typer.echo(json.dumps({"summary": summary}))


@app.command()
def notify(
    category: str = typer.Option("both", help="ai|cyber|both"),
    output_dir: Path = typer.Option(Path("out/emails"), help="Where to write email files"),
    no_send: bool = typer.Option(True, help="Only prepare files; sending is done in CI"),
):
    """Generate HTML + text email bodies for new jobs.

    Writes out/emails/{ai,cyber}.{html,txt}. Skips when there are no new jobs.
    """
    settings = Settings()
    ensure_dirs(settings)
    cats = ["ai", "cyber"] if category == "both" else [category]
    output_dir.mkdir(parents=True, exist_ok=True)

    any_output = False
    for c in cats:
        new_path = settings.data_dir / "latest" / f"new_{c}_jobs.json"
        if not new_path.exists():
            continue
        jobs_data = json.loads(new_path.read_text(encoding="utf-8"))
        jobs = [Job(**j) for j in jobs_data]
        if not jobs:
            continue
        count = len(jobs)
        subject = make_subject(c, count)
        html, text = render_email_bodies(c, jobs)
        (output_dir / f"{c}.html").write_text(html, encoding="utf-8")
        (output_dir / f"{c}.txt").write_text(text, encoding="utf-8")
        # Write a small meta file with subject + count for CI to consume
        meta = {"category": c, "count": count, "subject": subject}
        (output_dir / f"{c}.meta.json").write_text(json.dumps(meta), encoding="utf-8")
        typer.echo(subject)
        any_output = True

    if not any_output:
        typer.echo("No new jobs; no email files produced.")


@app.command("build-site")
def build_site():
    """Copy latest JSONs into docs/data for GitHub Pages."""
    settings = Settings()
    ensure_dirs(settings)
    sync_docs_data(settings, "ai")
    sync_docs_data(settings, "cyber")
    typer.echo("Site data updated.")


@app.command()
def validate():
    """Quick checks for expected files and configuration."""
    settings = Settings()
    ensure_dirs(settings)
    ok = True
    for p in [
        settings.data_dir / "state",
        settings.data_dir / "history" / "ai",
        settings.data_dir / "history" / "cyber",
        settings.data_dir / "latest",
        settings.docs_data_dir,
    ]:
        if not p.exists():
            typer.secho(f"Missing: {p}", fg=typer.colors.RED)
            ok = False
    if ok:
        typer.secho("Validate: OK", fg=typer.colors.GREEN)
    raise typer.Exit(code=0 if ok else 1)


if __name__ == "__main__":
    app()
