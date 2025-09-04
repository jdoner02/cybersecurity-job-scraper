# Notifications Setup

This project can notify users about new jobs via Discord and GitHub Discussions. You can use either or both.

## Discord

Two delivery methods are supported:

- Webhook (simple)
  - In your Discord server, go to the channel → Integrations → Webhooks → New Webhook.
  - Copy the webhook URL and add it as a repo secret: `DISCORD_WEBHOOK_URL`.
  - The workflow posts a summary embed with a direct link to the job board.

- Bot (advanced)
  - Create an application: https://discord.com/developers → Add a Bot → copy token.
  - Invite the bot to your server with permissions to read/send messages in the target channel.
  - Enable Developer Mode in Discord → Right‑click the target channel → Copy ID.
  - Add secrets: `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID`.
  - Optional: Use the CLI to post per‑job detailed embeds and maintain state to avoid duplicates.

CLI commands:

- Summary (webhook and/or bot):
  - `python -m ai_cyberjobs.cli send-notifications --site-url auto`

- Detailed per‑job drops (bot only):
  - `python -m ai_cyberjobs.cli send-detailed-discord --max-jobs-per-category 10`

## GitHub Discussions (email)

1. Enable Discussions in repository settings.
2. Create or choose a category (e.g., “Job Notifications”).
3. Get the category ID (`DIC_...`):
   - `GITHUB_TOKEN=... python scripts/get_discussion_categories.py <owner> <repo>`
4. Add repo secret `DISCUSSION_CATEGORY_ID` with that ID.
5. Users subscribe via Watch → Custom → check “Discussions” to receive email updates.

CLI commands:

- Summary post: created automatically by CI when data changes.
- One‑off detailed post: `python -m ai_cyberjobs.cli post-discussion-detailed --max-jobs-per-category 10 --site-url auto`

