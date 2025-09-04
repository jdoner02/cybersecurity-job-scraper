from __future__ import annotations

import json
from pathlib import Path
import os

import typer

from .config import Category, Settings, ensure_dirs
from .models import Job
from .notify.format import make_subject, render_email_bodies
from .notify.notify import notify_job_update
from .notify.discord_detailed import send_detailed_discord_notifications
from .notify.discussions import (
    format_job_update_discussion_detailed,
    create_discussion_post,
    discussion_already_posted,
    discussion_for_date_exists,
    mark_discussion_posted,
)
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
        settings=settings,
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


@app.command("post-discussion-detailed")
def post_discussion_detailed(
    max_jobs_per_category: int = typer.Option(10, help="Max jobs to list per category"),
    site_url: str = typer.Option(
        "auto",
        help="Job board URL or 'auto' to derive https://<owner>.github.io/<repo>",
    ),
    discussion_category: str = typer.Option(
        "",
        help="Override Discussion category ID; otherwise uses DISCUSSION_CATEGORY_ID env/setting",
    ),
) -> None:
    """Create a detailed GitHub Discussion post listing NEW jobs found today.

    Only posts when there are actual new jobs found during the current scrape run.
    Uses the new_{category}_jobs.json files to determine if there are new jobs.
    """
    settings = Settings()  # type: ignore[call-arg]
    ensure_dirs(settings)

    # Skip if already posted today (local marker or remote API check)
    from datetime import datetime

    today = datetime.utcnow()
    repo_env = os.getenv("GITHUB_REPOSITORY")
    owner = ""
    repo = ""
    if repo_env and "/" in repo_env:
        owner, repo = repo_env.split("/", 1)
    else:
        owner, repo = "jdoner02", "cybersecurity-job-scraper"

    if discussion_already_posted(today) or discussion_for_date_exists(owner, repo, today):
        typer.secho("Daily discussion already exists (guard); skipping.", fg=typer.colors.YELLOW)
        return

    # Load NEW jobs (not all jobs) from today's scrape
    new_ai_file = settings.data_dir / "latest" / "new_ai_jobs.json"
    new_cyber_file = settings.data_dir / "latest" / "new_cyber_jobs.json"
    
    # Check if we have any new jobs at all
    new_ai_jobs = []
    new_cyber_jobs = []
    
    if new_ai_file.exists():
        new_ai_jobs = json.loads(new_ai_file.read_text(encoding="utf-8"))
    if new_cyber_file.exists():
        new_cyber_jobs = json.loads(new_cyber_file.read_text(encoding="utf-8"))
    
    total_new_jobs = len(new_ai_jobs) + len(new_cyber_jobs)
    
    if total_new_jobs == 0:
        typer.secho("No new jobs found today; skipping discussion post.", fg=typer.colors.YELLOW)
        return
    
    typer.secho(f"Found {len(new_ai_jobs)} new AI jobs and {len(new_cyber_jobs)} new cyber jobs", fg=typer.colors.GREEN)

    # For discussion posting, we still use the full latest datasets (to show context)
    # but we only post when there are new jobs
    ai_file = settings.data_dir / "latest" / "ai_jobs.json"
    cyber_file = settings.data_dir / "latest" / "cyber_jobs.json"
    if not ai_file.exists() or not cyber_file.exists():
        typer.secho("Missing latest job files. Run scrape/build-site first.", fg=typer.colors.RED)
        raise typer.Exit(1)

    ai_jobs = json.loads(ai_file.read_text(encoding="utf-8"))
    cyber_jobs = json.loads(cyber_file.read_text(encoding="utf-8"))
    if not isinstance(ai_jobs, list):
        ai_jobs = ai_jobs.get("jobs", [])
    if not isinstance(cyber_jobs, list):
        cyber_jobs = cyber_jobs.get("jobs", [])

    # Derive repo for site URL
    repo_env = os.getenv("GITHUB_REPOSITORY")
    owner_env = os.getenv("GITHUB_OWNER")
    repo_name_env = os.getenv("GITHUB_REPO")
    if owner_env and repo_name_env:
        owner, repo = owner_env, repo_name_env
    elif repo_env and "/" in repo_env:
        owner, repo = repo_env.split("/", 1)
    else:
        owner, repo = "jdoner02", "cybersecurity-job-scraper"

    if site_url.strip().lower() == "auto":
        site_url = f"https://{owner}.github.io/{repo}"

    discussion_category = discussion_category or settings.discussion_category_id
    if not discussion_category:
        typer.secho("No Discussion category ID provided or configured.", fg=typer.colors.RED)
        raise typer.Exit(1)

    title, body = format_job_update_discussion_detailed(
        ai_jobs=ai_jobs,
        cyber_jobs=cyber_jobs,
        site_url=site_url,
        max_per_category=max_jobs_per_category,
    )

    discussion = create_discussion_post(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
        category_id=discussion_category,
    )

    if discussion:
        typer.secho(f"Created discussion: {discussion['url']}", fg=typer.colors.GREEN)
        mark_discussion_posted()
    else:
        typer.secho("Failed to create discussion.", fg=typer.colors.RED)


@app.command("send-detailed-discord")
def send_detailed_discord(
    max_jobs_per_category: int = typer.Option(
        10, help="Maximum number of jobs to post per category (AI/Cyber)"
    ),
) -> None:
    """Send detailed Discord notifications with individual job postings.

    This command posts individual job details to Discord, tracking which jobs
    have been posted before to avoid duplicates. Shows job titles, descriptions,
    organizations, locations, salaries, and apply links.
    """
    settings = Settings()  # type: ignore[call-arg]

    typer.echo("Sending detailed Discord job notifications...")

    results = send_detailed_discord_notifications(settings)

    success_count = sum(results.values())
    total_count = len(results)

    if success_count == total_count:
        typer.secho(
            f"✅ Detailed notifications sent successfully for all {total_count} categories",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            f"⚠️  {success_count}/{total_count} categories sent successfully", fg=typer.colors.YELLOW
        )
        for category, success in results.items():
            status = "✅" if success else "❌"
            typer.echo(f"  {status} {category.upper()} jobs")


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
