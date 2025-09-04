from __future__ import annotations

import json
from pathlib import Path

import typer

from .config import Category, Settings, ensure_dirs
from .models import Job
from .notify.format import make_subject, render_email_bodies
from .notify.notify import notify_job_update
from .pipeline.dedupe import compute_new_jobs, save_known_ids
from .pipeline.fetch import fetch_category
from .pipeline.store import (
    sync_docs_data,
    write_history_snapshot,
    write_latest,
    write_new_jobs,
)

app = typer.Typer(add_completion=False, help="AI & Cybersecurity USAJOBS scraper")


@app.command()
def scrape(
    category: str = typer.Option("both", help="ai|cyber|both"),
    days: int = typer.Option(None, help="Lookback days window"),
    limit: int = typer.Option(None, help="Max results to fetch per category"),
    dry_run: bool = typer.Option(False, help="Do not write outputs/state"),
) -> None:
    """Fetch jobs for a category and update data/state/history.

    If dry-run, prints a summary and writes nothing.
    """
    settings = Settings()  # type: ignore[call-arg]
    ensure_dirs(settings)
    days = days or settings.default_days
    limit = limit or settings.results_limit

    cats: list[Category] = ["ai", "cyber"] if category == "both" else [category]  # type: ignore[list-item]
    summary: dict[str, int] = {}
    for c in cats:
        jobs = fetch_category(settings, c, days=days, limit=limit)
        new_jobs, all_ids = compute_new_jobs(settings, c, jobs)
        summary[c] = len(new_jobs)
        if dry_run:
            typer.secho(
                f"[dry-run] {c}: {len(jobs)} jobs, {len(new_jobs)} new", fg=typer.colors.YELLOW
            )
            continue
        if new_jobs:
            write_latest(settings, c, jobs)
            write_history_snapshot(settings, c, jobs)
            write_new_jobs(settings, c, new_jobs)
            save_known_ids(settings, c, all_ids)
            sync_docs_data(settings, c)
            typer.echo(f"{c}: {len(jobs)} jobs, {len(new_jobs)} new")
        else:
            typer.echo(f"{c}: {len(jobs)} jobs, 0 new (no writes)")

    typer.echo(json.dumps({"summary": summary}))


@app.command()
def notify(
    category: str = typer.Option("both", help="ai|cyber|both"),
    output_dir: Path = typer.Option(Path("out/emails"), help="Where to write email files"),
    no_send: bool = typer.Option(True, help="Only prepare files; sending is done in CI"),
) -> None:
    """Generate HTML + text email bodies for new jobs.

    Writes out/emails/{ai,cyber}.{html,txt}. Skips when there are no new jobs.
    """
    settings = Settings()  # type: ignore[call-arg]
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


@app.command("send-notifications")
def send_notifications(
    site_url: str = typer.Option(
        "auto",
        help=(
            "Job board URL. Use 'auto' to derive as https://<owner>.github.io/<repo> "
            "from GITHUB_REPOSITORY or GITHUB_OWNER/GITHUB_REPO envs."
        ),
    ),
    discussion_category: str = typer.Option(
        "",
        help=(
            "GitHub Discussion category ID (optional). If omitted, uses env "
            "DISCUSSION_CATEGORY_ID. Leave empty to skip Discussions."
        ),
    ),
) -> None:
    """Send notifications via GitHub Discussions and Discord for current job counts."""
    settings = Settings()  # type: ignore[call-arg]

    # Count current jobs
    ai_path = settings.data_dir / "latest" / "ai_jobs.json"
    cyber_path = settings.data_dir / "latest" / "cyber_jobs.json"

    ai_count = 0
    cyber_count = 0

    if ai_path.exists():
        ai_data = json.loads(ai_path.read_text(encoding="utf-8"))
        ai_count = len(ai_data)

    if cyber_path.exists():
        cyber_data = json.loads(cyber_path.read_text(encoding="utf-8"))
        cyber_count = len(cyber_data)

    typer.echo(f"Sending notifications: {ai_count} AI jobs, {cyber_count} cyber jobs")

    results = notify_job_update(
        ai_count=ai_count,
        cyber_count=cyber_count,
        site_url=site_url,
        discussion_category_id=discussion_category,
    )

    success_count = sum(results.values())
    total_count = len(results)

    if success_count == total_count:
        typer.secho(f"✅ All {total_count} notifications sent successfully", fg=typer.colors.GREEN)
    else:
        typer.secho(f"⚠️  {success_count}/{total_count} notifications sent", fg=typer.colors.YELLOW)
        for channel, success in results.items():
            status = "✅" if success else "❌"
            typer.echo(f"  {status} {channel}")


@app.command("build-site")
def build_site() -> None:
    """Copy latest JSONs into docs/data for GitHub Pages."""
    settings = Settings()  # type: ignore[call-arg]
    ensure_dirs(settings)
    sync_docs_data(settings, "ai")
    sync_docs_data(settings, "cyber")
    typer.echo("Site data updated.")


@app.command()
def validate() -> None:
    """Quick checks for expected files and configuration."""
    settings = Settings()  # type: ignore[call-arg]
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
