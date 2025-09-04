"""Script to list GitHub Discussion category IDs for a repository.

Usage:
  GITHUB_TOKEN=... python scripts/get_discussion_categories.py [owner] [repo]

If owner/repo are omitted, tries to derive from GITHUB_REPOSITORY. Falls back to
prompting if not available.
"""

import os
import sys
import requests
import json


def get_discussion_categories(owner: str, repo: str, token: str):
    """Get discussion categories for a repository using GraphQL API.

    Returns a list of category nodes with id, name, description, and emoji.
    """

    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        discussionCategories(first: 10) {
          nodes {
            id
            name
            description
            emoji
            emojiHTML
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    variables = {
        "owner": owner,
        "repo": repo,
    }

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables},
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print("GraphQL errors:", data["errors"])
            return None
        return data["data"]["repository"]["discussionCategories"]["nodes"]
    else:
        print(f"HTTP error {response.status_code}: {response.text}")
        return None


def main():
    """Main function to get discussion categories."""
    # You'll need a GitHub token with repo permissions
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Please set GITHUB_TOKEN environment variable")
        print("Go to: https://github.com/settings/tokens")
        print("Create a token with 'repo' and 'read:discussion' permissions")
        return

    # Resolve owner/repo
    owner = None
    repo = None
    if len(sys.argv) >= 3:
        owner, repo = sys.argv[1], sys.argv[2]
    else:
        gh_repo = os.getenv("GITHUB_REPOSITORY")
        if gh_repo and "/" in gh_repo:
            owner, repo = gh_repo.split("/", 1)
    if not owner or not repo:
        print("Usage: python scripts/get_discussion_categories.py <owner> <repo>")
        return

    print(f"Getting discussion categories for {owner}/{repo}...")
    categories = get_discussion_categories(owner, repo, token)

    if categories:
        print("\nAvailable Discussion Categories:")
        print("=" * 50)
        for category in categories:
            print(f"Name: {category['name']}")
            print(f"ID: {category['id']}")
            print(f"Description: {category['description']}")
            print(f"Emoji: {category['emoji']}")
            print("-" * 30)

        # Look for job-related category
        job_categories = [
            c
            for c in categories
            if any(
                keyword in c["name"].lower() for keyword in ["job", "notification", "announcement"]
            )
        ]

        if job_categories:
            print("\n🎯 Recommended category for job notifications:")
            category = job_categories[0]
            print(f"Category: {category['name']}")
            print(f"ID: {category['id']}")
            print(f"\nAdd this to your GitHub repository secrets:")
            print(f"DISCUSSION_CATEGORY_ID = {category['id']}")
    else:
        print("Failed to get discussion categories")


if __name__ == "__main__":
    main()
