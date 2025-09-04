"""GitHub Discussions notification system."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests


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

    # GraphQL mutation to create discussion
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

    # First get repository ID
    repo_query = """
    query GetRepository($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 20) {
          nodes {
            id
            name
            slug
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }

    # Get repository ID and categories
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": repo_query, "variables": {"owner": owner, "name": repo}},
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Failed to get repository info: {response.status_code}")
        return None

    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None

    repository_id = data["data"]["repository"]["id"]

    # Create discussion
    response = requests.post(
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
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Failed to create discussion: {response.status_code}")
        return None

    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None

    return data["data"]["createDiscussion"]["discussion"]


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

### 📊 Data Source
All positions are sourced from USAJOBS.gov with a 30-day search window, updated daily via automated workflows.

---
*This update was generated automatically. Watch this repository to receive notifications for new job postings.*"""

    return title, body
