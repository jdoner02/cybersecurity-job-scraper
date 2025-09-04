"""Detailed Discord notifications with job tracking and individual job posts."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from ..config import Settings
from ..models import Job


def load_posted_jobs_state(settings: Settings) -> dict[str, set[str]]:
    """Load the state of which jobs have been posted to Discord.

    Returns:
        Dict with 'ai' and 'cyber' keys, each containing a set of job IDs that have been posted
    """
    state_file = settings.data_dir / "state" / "discord_posted.json"
    if not state_file.exists():
        return {"ai": set(), "cyber": set()}

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "ai": set(data.get("ai", [])),
            "cyber": set(data.get("cyber", [])),
        }
    except (json.JSONDecodeError, KeyError):
        return {"ai": set(), "cyber": set()}


def save_posted_jobs_state(settings: Settings, state: dict[str, set[str]]) -> None:
    """Save the state of which jobs have been posted to Discord."""
    state_file = settings.data_dir / "state" / "discord_posted.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert sets to lists for JSON serialization
    serializable_state = {category: list(job_ids) for category, job_ids in state.items()}

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(serializable_state, f, indent=2)


def create_job_detail_embed(job: Job, category: str) -> dict[str, Any]:
    """Create a detailed Discord embed for a single job."""
    # Truncate description if too long for Discord embed limits
    description = job.description
    if len(description) > 2000:
        description = description[:1997] + "..."

    # Create the embed
    embed = {
        "title": job.title,
        "description": description,
        "color": 0x3498DB if category == "ai" else 0xE74C3C,  # Blue for AI, Red for Cyber
        "fields": [
            {
                "name": "🏢 Organization",
                "value": job.organization,
                "inline": True,
            },
            {
                "name": "📍 Location",
                "value": ", ".join(job.locations) if job.locations else "Location not specified",
                "inline": True,
            },
        ],
        "url": str(job.url),
        "footer": {
            "text": f"USAJOBS.gov • {category.upper()} Position",
        },
        "timestamp": datetime.now().isoformat(),
    }

    # Add salary if available
    if job.salary:
        embed["fields"].append(
            {
                "name": "💰 Salary",
                "value": job.salary,
                "inline": True,
            }
        )

    # Add grade if available
    if job.grade:
        embed["fields"].append(
            {
                "name": "📊 Grade",
                "value": job.grade,
                "inline": True,
            }
        )

    # Add remote work info if available
    if job.remote is not None:
        embed["fields"].append(
            {
                "name": "🏠 Remote Work",
                "value": "Yes" if job.remote else "No",
                "inline": True,
            }
        )

    return embed


def send_discord_bot_detailed_jobs(
    new_jobs: list[Job],
    category: str,
    settings: Settings,
    max_jobs: int = 10,
) -> bool:
    """Send detailed job postings to Discord via bot.

    Args:
        new_jobs: List of new jobs to post
        category: 'ai' or 'cyber'
        settings: Settings object with Discord configuration
        max_jobs: Maximum number of jobs to post (default 10)

    Returns:
        True if successful, False otherwise
    """
    if not settings.discord_bot_token or not settings.discord_channel_id:
        print(f"No Discord bot configuration found for {category} jobs")
        return False

    if not new_jobs:
        print(f"No new {category} jobs to post")
        return True

    # Limit to max_jobs most recent
    jobs_to_post = new_jobs[:max_jobs]
    remaining_count = len(new_jobs) - len(jobs_to_post)

    headers = {
        "Authorization": f"Bot {settings.discord_bot_token}",
        "Content-Type": "application/json",
    }

    api_url = f"https://discord.com/api/v10/channels/{settings.discord_channel_id}/messages"

    try:
        # Send summary message if there are many jobs
        if remaining_count > 0:
            summary_content = (
                f"🚨 **{len(new_jobs)} New {category.upper()} Jobs Available!** 🚨\n\n"
                f"Showing the **{len(jobs_to_post)} most recent** positions below. "
                f"**{remaining_count} additional jobs** are available on the job board.\n\n"
                f"📋 View all jobs: https://jdoner02.github.io/cybersecurity-job-scraper"
            )
        else:
            summary_content = f"🚨 **{len(jobs_to_post)} New {category.upper()} Job{'s' if len(jobs_to_post) > 1 else ''} Available!** 🚨"

        # Send summary message
        summary_payload = {"content": summary_content}
        response = requests.post(api_url, json=summary_payload, headers=headers, timeout=30)
        response.raise_for_status()

        # Send individual job embeds
        for job in jobs_to_post:
            embed = create_job_detail_embed(job, category)

            apply_button_text = "🔗 **Apply Now**" if embed.get("url") else ""
            content = f"{apply_button_text}\n{embed['url']}" if embed.get("url") else ""

            payload = {
                "embeds": [embed],
                "content": content if content else None,
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            # Small delay to avoid rate limiting
            import time

            time.sleep(1)

        print(f"Successfully posted {len(jobs_to_post)} {category} jobs to Discord")
        return True

    except requests.RequestException as e:
        print(f"Failed to send {category} jobs to Discord: {e}")
        return False


def get_new_jobs_for_category(
    category: str, settings: Settings, posted_state: dict[str, set[str]]
) -> list[Job]:
    """Get new jobs for a category that haven't been posted to Discord yet.

    Args:
        category: 'ai' or 'cyber'
        settings: Settings object
        posted_state: State of which jobs have been posted

    Returns:
        List of new Job objects
    """
    jobs_file = settings.data_dir / "latest" / f"{category}_jobs.json"
    if not jobs_file.exists():
        return []

    try:
        with open(jobs_file, "r", encoding="utf-8") as f:
            jobs_data = json.load(f)

        # Convert to Job objects
        jobs = [Job(**job_data) for job_data in jobs_data]

        # Filter out jobs that have already been posted
        posted_ids = posted_state.get(category, set())
        new_jobs = [job for job in jobs if job.job_id not in posted_ids]

        # Sort by posting date (most recent first)
        new_jobs.sort(
            key=lambda job: (
                job.posted_at
                if isinstance(job.posted_at, datetime)
                else (
                    datetime.combine(job.posted_at, datetime.min.time())
                    if job.posted_at
                    else datetime.min
                )
            ),
            reverse=True,
        )

        return new_jobs

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading {category} jobs: {e}")
        return []


def send_detailed_discord_notifications(settings: Settings | None = None) -> dict[str, bool]:
    """Send detailed job notifications to Discord with individual job details.

    This function:
    1. Loads the state of which jobs have been posted before
    2. Finds new jobs that haven't been posted
    3. Posts up to 10 most recent jobs per category with full details
    4. Updates the state to track posted jobs

    Returns:
        Dict with success status for each category
    """
    if settings is None:
        settings = Settings()

    if not settings.discord_bot_token or not settings.discord_channel_id:
        print("Discord bot not configured for detailed notifications")
        return {"ai": False, "cyber": False}

    # Load state of previously posted jobs
    posted_state = load_posted_jobs_state(settings)
    results = {}

    for category in ["ai", "cyber"]:
        try:
            # Get new jobs for this category
            new_jobs = get_new_jobs_for_category(category, settings, posted_state)

            if new_jobs:
                # Send the jobs to Discord
                success = send_discord_bot_detailed_jobs(new_jobs, category, settings)

                if success:
                    # Update state to mark these jobs as posted
                    new_job_ids = {job.job_id for job in new_jobs}
                    posted_state[category].update(new_job_ids)

                results[category] = success
            else:
                print(f"No new {category} jobs found")
                results[category] = True  # No jobs to send is considered success

        except Exception as e:
            print(f"Error processing {category} jobs: {e}")
            results[category] = False

    # Save updated state
    try:
        save_posted_jobs_state(settings, posted_state)
    except Exception as e:
        print(f"Warning: Failed to save posted jobs state: {e}")

    return results
