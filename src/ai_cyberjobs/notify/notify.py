"""Notification systems for job updates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .discord import notify_job_update_discord
from .discussions import create_discussion_post, format_job_update_discussion


def notify_job_update(
    ai_count: int,
    cyber_count: int,
    site_url: str = "https://jdoner02.github.io/cybersecurity-job-scraper",
    discussion_category_id: str = "DIC_kwDONJKdhM4CjCr7",  # Default: General
    date: datetime | None = None,
) -> dict[str, bool]:
    """Send job update notifications via multiple channels.

    Args:
        ai_count: Number of AI jobs
        cyber_count: Number of cyber jobs
        site_url: URL to job board
        discussion_category_id: GitHub Discussion category ID
        date: Update date (defaults to now)

    Returns:
        Dict with success status for each notification type
    """
    results = {}

    # GitHub Discussion
    try:
        title, body = format_job_update_discussion(ai_count, cyber_count, site_url, date)
        discussion = create_discussion_post(
            owner="jdoner02",
            repo="cybersecurity-job-scraper",
            title=title,
            body=body,
            category_id=discussion_category_id,
        )
        results["discussion"] = discussion is not None
        if discussion:
            print(f"Created discussion: {discussion['url']}")
    except Exception as e:
        print(f"Discussion notification failed: {e}")
        results["discussion"] = False

    # Discord webhook
    try:
        discord_success = notify_job_update_discord(ai_count, cyber_count, site_url, date=date)
        results["discord"] = discord_success
        if discord_success:
            print("Discord notification sent successfully")
    except Exception as e:
        print(f"Discord notification failed: {e}")
        results["discord"] = False

    return results
