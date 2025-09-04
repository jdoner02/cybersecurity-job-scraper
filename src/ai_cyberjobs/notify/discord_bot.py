"""Discord Bot notification via REST API.

Uses a Bot token (no gateway connection) to post to a channel.
Relies only on `requests`, not `discord.py`.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests

from .discord import create_job_update_embed


API_BASE = "https://discord.com/api/v10"


def send_discord_bot_message(
    token: str,
    channel_id: str,
    content: str | None = None,
    embed: dict[str, Any] | None = None,
) -> bool:
    """Send a message to a Discord channel using a Bot token.

    Args:
        token: Discord Bot token ("Bot <token>" is applied automatically)
        channel_id: Target channel ID
        content: Plain text content
        embed: Optional single embed payload

    Returns:
        True on success, False otherwise
    """
    if not token:
        print("No Discord bot token provided")
        return False
    if not channel_id:
        print("No Discord channel ID provided")
        return False

    url = f"{API_BASE}/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {}
    if content:
        payload["content"] = content
    if embed:
        payload["embeds"] = [embed]

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Discord bot send failed: {e}")
        return False


def notify_job_update_discord_bot(
    ai_count: int,
    cyber_count: int,
    site_url: str,
    *,
    token: str | None = None,
    channel_id: str | None = None,
    date: datetime | None = None,
) -> bool:
    """Send job update via Discord Bot if configured.

    Looks up `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` from the environment
    when not explicitly provided. Returns False when not configured.
    """
    token = token or os.getenv("DISCORD_BOT_TOKEN")
    channel_id = channel_id or os.getenv("DISCORD_CHANNEL_ID")

    if not token or not channel_id:
        # Not configured; treat as a no-op success=False so callers can report status
        print("No Discord bot configuration found; skipping bot notification")
        return False

    embed = create_job_update_embed(ai_count, cyber_count, site_url, date)
    content = (
        f"**{ai_count + cyber_count} new government tech jobs** available! "
        f"Browse them here: {site_url}"
    )
    return send_discord_bot_message(token, channel_id, content=content, embed=embed)

