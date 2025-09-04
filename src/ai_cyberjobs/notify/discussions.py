"""GitHub Discussions notification system."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
from pathlib import Path

def _discussion_state_path() -> Path:
    return Path("data/state/discussion_posted.json")

def discussion_already_posted(today: datetime | None = None) -> bool:
    today = today or datetime.utcnow()
    p = _discussion_state_path()
    if not p.exists():
        return False
    try:
        data = p.read_text(encoding="utf-8").strip().splitlines()
        return today.strftime("%Y-%m-%d") in data
    except Exception:
        return False

def mark_discussion_posted(today: datetime | None = None) -> None:
    today = today or datetime.utcnow()
    p = _discussion_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    date_str = today.strftime("%Y-%m-%d")
    existing: set[str] = set()
    if p.exists():
        try:
            existing.update(p.read_text(encoding="utf-8").splitlines())
        except Exception:
            pass
    if date_str not in existing:
        existing.add(date_str)
        p.write_text("\n".join(sorted(existing)), encoding="utf-8")


def create_discussion_post(
    owner: str,
    repo: str,
    title: str,
    body: str,
    category_id: str,
    token: str | None = None,
) -> dict[str, Any] | None:
    """Create a GitHub Discussion post.

    Args:
        owner: Repository owner
        repo: Repository name
        title: Discussion title
        body: Discussion body (markdown)
        category_id: Discussion category ID
        token: GitHub token (uses GITHUB_TOKEN env if not provided)

    Returns:
        Discussion data or None if failed
    """
    token = token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("No GitHub token available")
        return None

    # Show token scopes (best effort) for debugging permissions
    try:
        scope_resp = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )
        scopes = scope_resp.headers.get("X-OAuth-Scopes", "(unavailable)")
        print(f"GitHub token scopes: {scopes}")
    except Exception as e:  # pragma: no cover - diagnostic only
        print(f"Could not retrieve token scopes: {e}")

    # --- Attempt REST API first (simpler) ---
    rest_headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    rest_payload = {"title": title, "body": body, "category_id": category_id}
    rest_url = f"https://api.github.com/repos/{owner}/{repo}/discussions"
    rest_resp = requests.post(rest_url, json=rest_payload, headers=rest_headers, timeout=30)

    if rest_resp.status_code == 201:
        rj = rest_resp.json()
        print("Created discussion via REST API")
        return {
            "id": rj.get("node_id"),
            "number": rj.get("number"),
            "title": rj.get("title"),
            "url": rj.get("html_url"),
        }
    else:
        print(
            f"REST create discussion failed: {rest_resp.status_code} - {rest_resp.text[:200]}"
        )

    # If REST failed (e.g., missing scope), attempt GraphQL fallback
    mutation = """
    mutation CreateDiscussion($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
        repositoryId: $repositoryId,
        categoryId: $categoryId,
        title: $title,
        body: $body
      }) {
        discussion {
          id
          number
          title
          url
        }
      }
    }
    """

    repo_query = """
    query GetRepository($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 50) {
          nodes { id name slug }
        }
      }
    }
    """

    gql_headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }
    repo_resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": repo_query, "variables": {"owner": owner, "name": repo}},
        headers=gql_headers,
        timeout=30,
    )
    if repo_resp.status_code != 200:
        print(f"GraphQL repo lookup failed: {repo_resp.status_code}")
        return None
    repo_data = repo_resp.json()
    if "errors" in repo_data:
        print(f"GraphQL repo errors: {repo_data['errors']}")
        return None
    repository_id = repo_data["data"]["repository"]["id"]

    create_resp = requests.post(
        "https://api.github.com/graphql",
        json={
            "query": mutation,
            "variables": {
                "repositoryId": repository_id,
                "categoryId": category_id,
                "title": title,
                "body": body,
            },
        },
        headers=gql_headers,
        timeout=30,
    )
    if create_resp.status_code != 200:
        print(f"GraphQL create failed: {create_resp.status_code}")
        return None
    create_data = create_resp.json()
    if "errors" in create_data:
        print(f"GraphQL errors: {create_data['errors']}")
        print(
            "Hint: Ensure your token has 'Discussions write' permission (classic PAT: repo/public_repo) "
            "or a fine-grained token with Discussions: Read & Write." 
        )
        return None
    return create_data["data"]["createDiscussion"]["discussion"]


def format_job_update_discussion(
    ai_count: int,
    cyber_count: int,
    site_url: str,
    date: datetime | None = None,
) -> tuple[str, str]:
    """Format job update for GitHub Discussion.

    Returns:
        Tuple of (title, body)
    """
    date = date or datetime.now()
    date_str = date.strftime("%B %d, %Y")

    title = f"Daily Job Update - {ai_count} AI jobs, {cyber_count} Cyber jobs - {date_str}"

    body = f"""## 🔍 Job Update for {date_str}

### Summary
- **AI Jobs**: {ai_count} positions available
- **Cybersecurity Jobs**: {cyber_count} positions available
- **Total**: {ai_count + cyber_count} new opportunities

### 🔗 View Jobs
Visit our [job board]({site_url}) to see all available positions with detailed descriptions, locations, and application links.

### � Get Email Notifications
To receive email notifications for future job updates:
1. **Watch this repository** by clicking the "Watch" button above
2. **Subscribe to discussions** in your GitHub notification settings
3. You'll get emails when new job discussion posts are created

### �📊 Data Source
All positions are sourced from USAJOBS.gov with a 30-day search window, updated daily via automated workflows.

---
*This update was generated automatically. Watch this repository and subscribe to discussions to receive email notifications for new job postings.*"""

    return title, body


def format_job_update_discussion_detailed(
    ai_jobs: list[dict],
    cyber_jobs: list[dict],
    site_url: str,
    max_per_category: int = 10,
    date: datetime | None = None,
) -> tuple[str, str]:
    """Format a more detailed discussion body including job titles & links.

    Args:
        ai_jobs: List of AI job dicts (expects keys: title, url)
        cyber_jobs: List of Cyber job dicts
        site_url: Job board URL
        max_per_category: Max jobs to list per category
        date: Optional date override

    Returns:
        (title, body) markdown
    """
    date = date or datetime.now()
    date_str = date.strftime("%B %d, %Y")
    ai_count = len(ai_jobs)
    cyber_count = len(cyber_jobs)

    title = f"Daily Job Update (Detailed) – {ai_count} AI / {cyber_count} Cyber – {date_str}"

    def _format_jobs(jobs: list[dict]):
        lines: list[str] = []
        for j in jobs[:max_per_category]:
            t = j.get("title", "(Untitled)")
            url = j.get("url") or site_url
            org = j.get("organization") or ""  # optional
            lines.append(f"- [{t}]({url}){f' – {org}' if org else ''}")
        if len(jobs) > max_per_category:
            lines.append(f"- … and {len(jobs) - max_per_category} more on the site")
        return "\n".join(lines) if lines else "(No jobs listed)"

    body = f"""## 🔍 Daily Job Update – {date_str}

### Summary
- **AI Jobs**: {ai_count}
- **Cybersecurity Jobs**: {cyber_count}
- **Total**: {ai_count + cyber_count}

### 🤖 AI (Top {min(max_per_category, ai_count)} of {ai_count})
{_format_jobs(ai_jobs)}

### 🔒 Cybersecurity (Top {min(max_per_category, cyber_count)} of {cyber_count})
{_format_jobs(cyber_jobs)}

### 🔗 Full Listings
Browse all details, filters, and apply links on the **[Job Board]({site_url})**.

### 📫 Subscribe / Emails
Watch this repository → Custom → enable *Discussions* to receive these updates via email.

---
*Automated post. Generated at {date.isoformat()}.*
"""

    return title, body


def get_discussion_subscription_info(
    owner: str,
    repo: str,
    token: str | None = None,
) -> dict[str, Any]:
    """Get information about subscribing to discussions for email notifications.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token (uses GITHUB_TOKEN env if not provided)
    
    Returns:
        Dict with subscription info and URLs
    """
    base_url = f"https://github.com/{owner}/{repo}"
    
    return {
        "repository_url": base_url,
        "discussions_url": f"{base_url}/discussions",
        "watch_url": f"{base_url}/subscription",
        "instructions": [
            "Visit the repository and click 'Watch' to enable notifications",
            "Go to GitHub Settings > Notifications to configure email preferences",
            "Subscribe to 'Discussions' to get emails for job updates",
            "You'll receive emails when new job discussion posts are created"
        ]
    }
