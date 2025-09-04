# AI & Cybersecurity Jobs – USAJOBS

Daily scraper that fetches AI and Cybersecurity roles from USAJOBS, stores versioned data (JSON/CSV), publishes a small mobile-friendly site via GitHub Pages, and sends concise email digests through GitHub Actions. It can also notify a Discord channel (Webhook or Bot) and post to GitHub Discussions so subscribers get emails.

Features
- Two categories: AI and Cybersecurity
- Detects new postings and only emails when there are additions
- Stores `data/latest/*.json|.csv` and daily snapshots under `data/history/*`
- Static site under `docs/` with searchable, mobile-friendly pages
# AI & Cybersecurity USAJOBS Tracker

Automated daily pipeline that fetches AI & Cybersecurity roles from USAJOBS, publishes a lightweight searchable site (GitHub Pages), and sends optional notifications (Discord + GitHub Discussions for email subscribers). Designed to be minimal, auditable, and easy to fork.

## Highlights
- AI + Cyber categories (separate feeds)
- Detects new jobs; only notifies when new records appear
- Daily snapshots in `data/history/` (for longitudinal analysis)
- Static site in `docs/` (mobile friendly)
- Discord (webhook + bot) + GitHub Discussions email posts
- Detailed Discord job drops (top N per category, deduped)
- Typed models, tests, ruff / black / mypy, pre-commit hooks
- Scrape AI: `python -m ai_cyberjobs.cli scrape --category ai`
## Quick Start
1. Python 3.11+
2. Create `.env` with `USAJOBS_EMAIL`, `USAJOBS_API_KEY`
3. Install: `make install`
4. Dry run: `python -m ai_cyberjobs.cli scrape --category both --limit 5 --dry-run`
5. Build site data: `python -m ai_cyberjobs.cli build-site`

## Common Commands
| Purpose | Command |
|---------|---------|
| Scrape AI | `python -m ai_cyberjobs.cli scrape --category ai` |
| Scrape Cyber | `python -m ai_cyberjobs.cli scrape --category cyber` |
| Generate (no send) email artifacts | `python -m ai_cyberjobs.cli notify --category both --no-send` |
| Send summary notifications | `python -m ai_cyberjobs.cli send-notifications --site-url auto` |
| Detailed Discord job posts | `python -m ai_cyberjobs.cli send-detailed-discord` |
| One‑off detailed Discussion | `python -m ai_cyberjobs.cli post-discussion-detailed --max-jobs-per-category 10` |
| Validate expected files | `python -m ai_cyberjobs.cli validate` |
  - `DEFAULT_DAYS` (default 2), `RESULTS_LIMIT` (default 50)
If credentials are absent the scraper returns zero jobs so you can still test the pipeline.
  - Discord Bot: `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`
## Configuration
Required:
- `USAJOBS_EMAIL` (User-Agent email)
- `USAJOBS_API_KEY`

Optional:
- `REQUESTS_TIMEOUT` (default 20)
- `RATE_LIMIT_PER_MIN` (default 10)
- `DEFAULT_DAYS` (default 2)
- `RESULTS_LIMIT` (default 50)
- Discord webhook: `DISCORD_WEBHOOK_URL`
- Discord bot: `DISCORD_BOT_TOKEN`, `DISCORD_CHANNEL_ID`
- GitHub Discussions: `DISCUSSION_CATEGORY_ID`
- Override site URL: `SITE_URL` or `--site-url`

## Automation (GitHub Actions)
Workflow: `.github/workflows/daily-scrape.yml`

Pipeline: scrape (AI + Cyber) → build-site → commit changes → notifications → (optional) email.

Daily Discussion & detailed Discord posts occur only when new jobs were detected that day (prevents spam). Manual dispatch (`workflow_dispatch`) can force a run; the Discussion logic still skips if no new jobs.

Email (optional): requires `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM` secrets.
  - Invite the bot to your server, grant Read/Send permissions in target channel.
## GitHub Pages
Serve `/docs` as Pages. JSON feeds auto-refresh there after each run.

## Discord
Webhook: only `DISCORD_WEBHOOK_URL`.

Bot (optional): `DISCORD_BOT_TOKEN` + `DISCORD_CHANNEL_ID` (channel ID from Developer Mode).

## GitHub Discussions (Email Subscription)
1. Enable Discussions in repo settings.
2. Create category “Job Notifications”.
3. Find its ID (`DIC_...`) via DevTools or script.
4. Set secret `DISCUSSION_CATEGORY_ID`.
5. Users: Watch → Custom → enable Discussions.
See also: `docs/notifications.md` for step‑by‑step setup with screenshots guidance.
Subscription Links:
- Discussions: https://github.com/jdoner02/cybersecurity-job-scraper/discussions
- Job Board: https://jdoner02.github.io/cybersecurity-job-scraper/
[![Subscribe – GitHub Discussions](https://img.shields.io/badge/Subscribe-Job%20Alerts-blue)](https://github.com/jdoner02/cybersecurity-job-scraper/discussions)
Advanced:
- Detailed Discord embeds: `send-detailed-discord`
- One-off detailed Discussion: `post-discussion-detailed`
```
See also: `docs/notifications.md` (optional extra detail).
  client/ (USAJOBS client)
Badge (optional):
```
[![Subscribe – GitHub Discussions](https://img.shields.io/badge/Subscribe-Job%20Alerts-blue)](https://github.com/jdoner02/cybersecurity-job-scraper/discussions)
```
docs/ (static site)
## Project Structure

Architecture (ASCII)
```
[queries] -> [USAJobsClient] -> raw -> [normalize] -> Job -> [dedupe] -> new
                                                            |            \
                                                            v             v
                                                         [store latest]  [write new_*]
                                                            |             \
                                                            v              v
                                                       [docs/data/*]     [notify -> out/emails/*]
## Data Flow
# AI & Cybersecurity Job Feed

**Live Board:** https://jdoner02.github.io/cybersecurity-job-scraper/  
**Subscribe (email via GitHub Discussions):** https://github.com/jdoner02/cybersecurity-job-scraper/discussions

## What This Is
Daily, automated collection of new U.S. federal job postings related to Artificial Intelligence and Cybersecurity (sourced from USAJOBS). Results are published to a simple, fast, mobile‑friendly site and an optional daily Discussion post you can follow for email updates.

## Who It’s For
Students exploring internships or early career roles.  
Faculty/advisors wanting a single, dependable link to share with cohorts.  
Anyone tracking federal AI & Cyber opportunities without manually searching.

## What You Get
- Fresh AI & Cyber job listings (titles, agencies, locations, links) updated each morning.
- One Discussion post per day (only if new jobs appeared) you can subscribe to for email notifications.
- Lightweight historical archive (trend potential; not emphasized here).

## How to Subscribe (Email)
1. Open the Discussions link above.
2. Click “Watch” → “Custom” → enable “Discussions”.
3. You’ll receive an email when the daily post appears (only on days with new jobs).

## Data & Schedule
- Source: USAJOBS public API (official federal listings).
- Update cadence: daily automated workflow (UTC morning).
- Filtering: focused keyword sets for AI and Cyber; tuned to avoid empty results while staying relevant.
- Privacy: no personal data stored—just public job metadata.

## Reliability Notes
- If USAJOBS is slow or rate limited, the run retries gracefully.
- A day with no new postings = no email (reduced inbox noise).

## Want to Contribute?
Minor improvements (keyword tuning, formatting, accessibility) are welcome. Open an Issue or small PR.

## License
MIT. Use freely for educational and advising purposes.

---
Helping students and faculty track federal AI & Cyber opportunities—concise and reliable.

