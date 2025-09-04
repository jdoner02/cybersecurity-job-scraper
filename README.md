# AI & Cybersecurity Jobs – USAJOBS

Daily scraper that fetches AI and Cybersecurity roles from USAJOBS, stores versioned data (JSON/CSV), publishes a small mobile-friendly site via GitHub Pages, and sends concise email digests through GitHub Actions. It can also notify a Discord channel (Webhook or Bot) and post to GitHub Discussions so subscribers get emails.

Features
- Two categories: AI and Cybersecurity
- Detects new postings and only emails when there are additions
- Stores `data/latest/*.json|.csv` and daily snapshots under `data/history/*`
- Static site under `docs/` with searchable, mobile-friendly pages
- Automated daily run + manual dispatch via GitHub Actions
- Discord notifications (Webhook and/or Bot)
- Optional GitHub Discussions posts (email via subscriptions)
- Detailed Discord job drops (individual embeds, de‑duped, up to 10 per category)
- SOLID/OOP/DRY, typed models, tests, ruff/black/mypy, pre-commit

Quickstart
- Python 3.11+ (the package requires >=3.11; if your system python is older install 3.11 via pyenv or asdf)
- `cp examples/.env.example .env` and fill in: `USAJOBS_EMAIL`, `USAJOBS_API_KEY`
- `make install`
- Dry run: `python -m ai_cyberjobs.cli scrape --category both --limit 5 --dry-run`
- Build site data: `python -m ai_cyberjobs.cli build-site`

Local usage
- Scrape AI: `python -m ai_cyberjobs.cli scrape --category ai`
- Scrape Cyber: `python -m ai_cyberjobs.cli scrape --category cyber`
- Notify (generates files, does not send): `python -m ai_cyberjobs.cli notify --category both --no-send`
- Send Discord + Discussions notifications: `python -m ai_cyberjobs.cli send-notifications --site-url auto`
- Validate structure: `python -m ai_cyberjobs.cli validate`

If credentials are not yet configured the scraper returns zero jobs instead of failing so you can still test the CLI & site pipeline.

Configuration
- Required env vars (via `.env` or CI secrets):
  - `USAJOBS_EMAIL` – your registered email with USAJOBS for User-Agent
  - `USAJOBS_API_KEY` – Authorization-Key header value
- Optional:
  - `REQUESTS_TIMEOUT` (default 20), `RATE_LIMIT_PER_MIN` (default 10)
  - `DEFAULT_DAYS` (default 2), `RESULTS_LIMIT` (default 50)
  - Discord Webhook: `DISCORD_WEBHOOK_URL`
  - Discord Bot: `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`
  - GitHub Discussions: `DISCUSSION_CATEGORY_ID`
  - Site URL override: `SITE_URL` or `--site-url` (defaults to `https://<owner>.github.io/<repo>`)

 Automation (GitHub Actions)
- Workflow: `.github/workflows/daily-scrape.yml`
- Triggers: daily cron (UTC) and `workflow_dispatch`
- Steps: checkout → setup python → install → `scrape` (AI, Cyber) → `build-site` → commit/push data changes → `notify` (generates email files) → send two emails via SMTP action (one per category) only if new jobs exist
  - Email subjects include counts, e.g. "New AI Jobs (N) – USAJOBS" and "New Cybersecurity Jobs (N) – USAJOBS".
- Required repository secrets for email delivery:
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`
- Permissions: `permissions: contents: write` to push data updates

GitHub Pages
- Configure Pages to serve from the `/docs` folder on the default branch
- The scraper updates `docs/data/{ai,cyber}_jobs.json` each run

Discord notifications
- Webhook (simple): create a channel webhook (Integrations → Webhooks) and set `DISCORD_WEBHOOK_URL` secret. No bot user required.
- Bot (posts as a real bot user):
  - Create an application at https://discord.com/developers → add a Bot, copy the token.
  - Invite the bot to your server, grant Read/Send permissions in target channel.
  - Enable Developer Mode in Discord → right‑click the channel → Copy ID.
  - Add repo secrets: `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`.
  - The workflow tries both: it uses the bot when configured, and/or the webhook when present.

GitHub Discussions (email by subscription)
- Enable Discussions: Repository Settings → General → Enable “Discussions”.
- Create a category (recommended: Announcement format) named **“Job Notifications”**.
- Find the category ID (starts with `DIC_`):
  - Option A: Open DevTools → Network → reload a discussion page → inspect GraphQL response for `category { id }`.
  - Option B: Run `python get_discussion_categories.py` with a temporary token (scopes: `repo`, `read:discussion`).
- Add repo secret `DISCUSSION_CATEGORY_ID=<that id>`.
- Users subscribe via: Watch button → Custom → check “Discussions”. They receive an email for each automated post.

Subscribe links
- GitHub Discussions (email): https://github.com/jdoner02/cybersecurity-job-scraper/discussions
- Job Board: https://jdoner02.github.io/cybersecurity-job-scraper/

Add a README badge (optional):
```
[![Subscribe – GitHub Discussions](https://img.shields.io/badge/Subscribe-Job%20Alerts-blue)](https://github.com/jdoner02/cybersecurity-job-scraper/discussions)
```

Project structure
```
src/ai_cyberjobs/
  client/ (USAJOBS client)
  pipeline/ (fetch, normalize, dedupe, store)
  notify/ (email formatting)
  cli.py (Typer CLI)
data/ (state, latest, history)
docs/ (static site)
```

Architecture (ASCII)
```
[queries] -> [USAJobsClient] -> raw -> [normalize] -> Job -> [dedupe] -> new
                                                            |            \
                                                            v             v
                                                         [store latest]  [write new_*]
                                                            |             \
                                                            v              v
                                                       [docs/data/*]     [notify -> out/emails/*]
```

Notes
- Emails are sent by GitHub Actions using SMTP; Python only generates bodies
- `send-notifications` auto‑derives the site URL from `GITHUB_REPOSITORY` (`https://<owner>.github.io/<repo>`). Override with `--site-url`.
- Before production, verify USAJOBS API headers/params against latest official docs
- No secrets are committed; use `.env` locally and CI secrets in GitHub
- Keyword strategy: empirically the USAJOBS search can return fewer (even zero) results
  when using long `term1 OR term2 OR term3` chains. Implementation now uses only the
  primary phrase (e.g. "artificial intelligence") when many AI keywords are configured
  to avoid over-filtering. With ≤4 terms it space-joins them for a broad match.


## 📧 Support

For questions about:
- **API Access**: Contact USAJobs developer support
- **NCAE Programs**: Consult your school's cybersecurity department
- **Federal Hiring**: Visit [help.usajobs.gov](https://help.usajobs.gov/)

## 📄 License

This project is provided as-is for educational and career development purposes for NCAE students and cybersecurity professionals.

## 🤝 Contributing

To improve the scraper:
1. Add new relevant keywords to the search criteria
2. Enhance filtering logic for better job relevance
3. Improve data export formats
4. Add new scheduling options

---

**Happy Job Hunting! 🔍💼**

*This tool helps you stay ahead of federal cybersecurity opportunities - perfect for launching your career in government cybersecurity roles.*
