"""Discord webhook notification system."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests


def send_discord_webhook(
    webhook_url: str,
    content: str | None = None,
    embeds: list[dict[str, Any]] | None = None,
) -> bool:
    """Send a Discord webhook notification.

    Args:
        webhook_url: Discord webhook URL
        content: Plain text content
        embeds: List of Discord embed objects

    Returns:
        True if successful, False otherwise
    """
    if not webhook_url:
        print("No Discord webhook URL provided")
        return False

    payload = {}
    if content:
        payload["content"] = content
    if embeds:
        payload["embeds"] = embeds

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Discord webhook failed: {e}")
        return False


def create_job_update_embed(
    ai_count: int,
    cyber_count: int,
    site_url: str,
    date: datetime | None = None,
) -> dict[str, Any]:
    """Create Discord embed for job update.

    Returns:
        Discord embed object
    """
    date = date or datetime.now()

    embed = {
        "title": "🔍 Daily Job Update",
        "description": f"New government tech jobs available as of {date.strftime('%B %d, %Y')}",
        "color": 0x61DAFB,  # Cyan blue
        "fields": [
            {
                "name": "🤖 AI Jobs",
                "value": str(ai_count),
                "inline": True,
            },
            {
                "name": "🔒 Cybersecurity Jobs",
                "value": str(cyber_count),
                "inline": True,
            },
            {
                "name": "📊 Total Opportunities",
                "value": str(ai_count + cyber_count),
                "inline": True,
            },
        ],
        "footer": {
            "text": "USAJOBS.gov • Updated daily",
        },
        "timestamp": date.isoformat(),
        "url": site_url,
    }

    return embed


def notify_job_update_discord(
    ai_count: int,
    cyber_count: int,
    site_url: str,
    webhook_url: str | None = None,
    date: datetime | None = None,
) -> bool:
    """Send job update notification to Discord.

    Args:
        ai_count: Number of AI jobs
        cyber_count: Number of cyber jobs
        site_url: URL to job board
        webhook_url: Discord webhook URL (uses DISCORD_WEBHOOK_URL env if not provided)
        date: Update date (defaults to now)

    Returns:
        True if successful, False otherwise
    """
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("No Discord webhook URL configured")
        return False

    embed = create_job_update_embed(ai_count, cyber_count, site_url, date)

    content = (
        f"**{ai_count + cyber_count} new government tech jobs** available! "
        f"Browse them here: {site_url}"
    )

    return send_discord_webhook(webhook_url, content, [embed])
