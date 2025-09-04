"""Notification systems for job updates.

This module coordinates multi-channel notifications (GitHub Discussions, Discord).
It supports both Discord Webhooks and a Discord Bot (token + channel ID).
"""

from __future__ import annotations

import os
from datetime import datetime

from ..config import Settings
from .discord import notify_job_update_discord
from .discord_bot import notify_job_update_discord_bot
from .discussions import create_discussion_post, format_job_update_discussion


def notify_job_update(
    ai_count: int,
    cyber_count: int,
    site_url: str | None = None,
    discussion_category_id: str | None = None,
    date: datetime | None = None,
    settings: Settings | None = None,
) -> dict[str, bool]:
    """Send job update notifications via multiple channels.

    Args:
        ai_count: Number of AI jobs
        cyber_count: Number of cyber jobs
        site_url: URL to job board (auto-derives from repo if not provided)
        discussion_category_id: GitHub Discussion category ID (if configured)
        date: Update date (defaults to now)
        settings: Settings object with Discord/notification configuration

    Returns:
        Dict with success status for each notification type
    """
    if settings is None:
        settings = Settings()

    results = {}

    # Derive owner/repo and site URL from environment where possible
    repo_env = os.getenv("GITHUB_REPOSITORY")  # e.g. "owner/repo"
    owner_env = os.getenv("GITHUB_OWNER")
    repo_name_env = os.getenv("GITHUB_REPO")

    if owner_env and repo_name_env:
        owner, repo = owner_env, repo_name_env
    elif repo_env and "/" in repo_env:
        owner, repo = repo_env.split("/", 1)
    else:
        # Fallback defaults; consider overriding via CLI/env for your repo
        owner, repo = "jdoner02", "cybersecurity-job-scraper"

    # Allow explicit override via env SITE_URL
    site_url = site_url or os.getenv("SITE_URL")
    if not site_url or site_url.strip().lower() == "auto":
        site_url = f"https://{owner}.github.io/{repo}"

    # GitHub Discussion
    try:
        # Allow configuration via env DISCUSSION_CATEGORY_ID if not provided
        discussion_category_id = discussion_category_id or settings.discussion_category_id
        if discussion_category_id:
            title, body = format_job_update_discussion(ai_count, cyber_count, site_url, date)
            discussion = create_discussion_post(
                owner=owner,
                repo=repo,
                title=title,
                body=body,
                category_id=discussion_category_id,
            )
            results["discussion"] = discussion is not None
            if discussion:
                print(f"Created discussion: {discussion['url']}")
        else:
            print("No Discussion category ID configured; skipping Discussions notification")
    except Exception as e:
        print(f"Discussion notification failed: {e}")
        results["discussion"] = False

    # Discord (Webhook)
    try:
        webhook_success = notify_job_update_discord(
            ai_count, cyber_count, site_url, webhook_url=settings.discord_webhook_url, date=date
        )
        if webhook_success:
            print("Discord (webhook) notification sent successfully")
        results["discord_webhook"] = webhook_success
    except Exception as e:
        print(f"Discord (webhook) notification failed: {e}")
        results["discord_webhook"] = False

    # Discord (Bot token + channel)
    try:
        bot_success = notify_job_update_discord_bot(
            ai_count,
            cyber_count,
            site_url,
            token=settings.discord_bot_token,
            channel_id=settings.discord_channel_id,
            date=date,
        )
        if bot_success:
            print("Discord (bot) notification sent successfully")
        results["discord_bot"] = bot_success
    except Exception as e:
        print(f"Discord (bot) notification failed: {e}")
        results["discord_bot"] = False

    return results
