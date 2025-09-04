ROLE
You are a senior Python engineer & open‑source maintainer (architect + infra). You work autonomously in the VS Code workspace provided. You will aggressively rebuild the project to a professional standard using SOLID, OOP, DRY, and appropriate design patterns. You will delete legacy AI‑generated code and replace it with a clean, tested, documented, automated solution.

CONTEXT
Workspace path: /Users/jessicadoner/Projects/job-scraper-demo
Current tree (delete/replace most files as directed below):
.
├── analyze_jobs.py
├── config.py
├── cybersecurity_scraper.py
├── demo.py
├── job_data
│   ├── active_cybersecurity_jobs.csv
│   ├── active_cybersecurity_jobs.json
│   ├── entry_level_cybersecurity_jobs.csv
│   ├── master_jobs_database.json
│   ├── no_clearance_cybersecurity_jobs.csv
│   └── scraping_stats.json
├── qualification_extractor.py
├── README.md
├── requirements.txt
├── scheduled_scraper.py
├── test_api_format.py
├── test_simple_scraper.py
└── usajobs_client.py

GOAL
Ship a production‑ready, modular Python package that:
1) Scrapes USAJOBS for two categories once per day:
   - **AI** (artificial intelligence, machine learning, NLP, LLMs, etc.)
   - **Cybersecurity**
2) Detects newly posted jobs and sends **two separate emails** (one for AI, one for Cybersecurity) to:
   - jdoner@ewu.edu
   - ssteiner@ewu.edu
   The email body is a compact list of: **Job Number/ID**, **one‑paragraph description/summary**, and a **direct apply link**.
3) Stores the latest job lists in the repo (versioned JSON and CSV), and publishes a **simple, mobile‑friendly front‑end** students can browse from phones/computers (GitHub Pages) with two pages: **AI Jobs** and **Cybersecurity Jobs**.
4) Runs automatically via **GitHub Actions** (daily on cron + manual dispatch). Commits data updates back to the repo using `GITHUB_TOKEN` with `contents: write` permissions.
5) Adheres to SOLID/OOP/DRY, with type hints, tests, linting, formatting, pre‑commit hooks, clear docs, and an example `.env`.

SECURITY & SECRETS
- **Do not commit `.env`.** Add a `.env.example` and `.gitignore`.
- Use these variable names (read via `python-dotenv` or `pydantic-settings`):
  - `USAJOBS_EMAIL`  (User-Agent email required by USAJOBS)
  - `USAJOBS_API_KEY` (API key)
  - Email sending (choose one path below):
    - If sending via Python SMTP: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`
    - Or via a GitHub Action (preferred if available): configure SMTP secrets as **repository secrets** and wire them in workflow.
- In GitHub Actions, set `permissions: contents: write` so the workflow can push data updates.

SCOPE & RULES
- **Aggressively replace** legacy code. Remove all root‑level legacy `.py` files and tests, and migrate any useful raw data from `job_data/` into the new `data/` layout before deleting `job_data/`.
- No interactive questions. Make reasonable, conservative defaults. Add TODOs or clear comments where human secrets/config are needed.
- Write clear commit messages. Prefer atomic commits per major step.
- Use Python **3.11+**.
- Package layout uses **PEP 621** metadata in `pyproject.toml` (setuptools) + `ruff` + `black` + `mypy` + `pytest` + `pytest-cov` + `pre-commit`.
- CLI built with **Typer**; HTTP via **requests**; settings via **pydantic-settings** (or python‑dotenv); data handling via stdlib + `pydantic` models.
- Front‑end is a static site (no backend) in `docs/` and is served by GitHub Pages (mobile‑friendly HTML + a tiny JS table viewer). The scraper writes `docs/data/ai_jobs.json` and `docs/data/cyber_jobs.json` each run.
- USAJOBS integration: Use the official REST API. **Before finalizing** the client, re‑verify the latest official USAJOBS API docs (auth headers and search params frequently evolve). Implement a robust client with retries, rate limiting, and typed models. Ensure the results include at least: job id/number, title, org, location(s), short summary/description, direct apply URL, posting date. Prefer API “updated since” filtering if available; otherwise dedupe via stored IDs + posted/updated dates.
- Email content is concise & readable (plain‑text fallback + HTML). It must list: job number, 1‑paragraph description (trimmed), and direct link. Separate messages for AI and Cyber.
- New jobs detection: persist a small state file of **known job IDs** per category to only email on additions.
- Automation: GitHub Actions runs daily on cron (UTC) and on manual dispatch. If new jobs exist, send the emails and push updated data + site JSONs. If no new jobs, exit cleanly without committing.

TARGET PROJECT STRUCTURE (create exactly this; replace legacy files)
.
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── .github/
│   └── workflows/
│       └── daily-scrape.yml
├── docs/                      # GitHub Pages static site
│   ├── index.html             # landing w/ two links
│   ├── ai.html                # AI jobs page
│   ├── cyber.html             # Cybersecurity jobs page
│   ├── assets/
│   │   ├── styles.css         # minimal responsive CSS
│   │   └── app.js             # fetch + render JSON tables (mobile friendly)
│   └── data/
│       ├── ai_jobs.json       # overwritten daily
│       └── cyber_jobs.json    # overwritten daily
├── data/
│   ├── state/
│   │   ├── known_ai_ids.json
│   │   └── known_cyber_ids.json
│   ├── history/
│   │   ├── ai/                # YYYY-MM-DD.json snapshots
│   │   └── cyber/
│   └── latest/
│       ├── ai_jobs.json
│       └── cyber_jobs.json
├── examples/
│   └── .env.example
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── src/
│   └── ai_cyberjobs/
│       ├── __init__.py
│       ├── config.py          # settings/env loading
│       ├── models.py          # pydantic models (Job, Query, Results, etc.)
│       ├── queries.py         # keyword strategies for AI & Cyber
│       ├── client/
│       │   ├── base.py        # interface/protocol for job clients
│       │   └── usajobs.py     # USAJOBS implementation (auth, pagination, retry)
│       ├── pipeline/
│       │   ├── fetch.py       # orchestration of searches per category
│       │   ├── normalize.py   # mapping API results → Job model, trimming summaries
│       │   ├── dedupe.py      # set logic for new IDs
│       │   └── store.py       # write JSON/CSV, update state/history, write docs/data
│       ├── notify/
│       │   ├── format.py      # compose email bodies (plain + html)
│       │   └── send.py        # SMTP sender (no-op if secrets are missing)
│       └── cli.py             # Typer CLI (scrape, notify, build-site, validate)
└── tests/
    ├── test_client_usajobs.py
    ├── test_pipeline_dedupe.py
    ├── test_store_io.py
    └── test_notify_format.py

KEY DESIGN REQUIREMENTS
- **SOLID/OOP/DRY**: 
  - Interface/Adapter pattern: `client.base: JobsClient` with `search(query) -> Iterator[Job]`.
  - Strategy for keyword sets: `queries.py` defines categories (`"ai"`, `"cyber"`) and their keyword lists (AI: artificial intelligence, AI, machine learning, ML, deep learning, NLP, LLM, generative, reinforcement learning; Cyber: cybersecurity, information security, infosec, SOC, threat, incident response, blue team, red team, penetration testing).
  - Repository pattern for persistence in `store.py`.
  - Config object via typed settings (`pydantic-settings`) to centralize env/secrets.
- **Data model** (`models.Job`):
  - `job_id: str` (canonical USAJOBS ID), `title: str`, `organization: str`, `locations: list[str]`, `description: str` (trim to ~600 chars, strip HTML), `url: HttpUrl`, `posted_at: date|datetime`, optional salary range/grade/remote flags if cheaply available.
- **Emails**:
  - Subject: `New AI Jobs (N) – USAJOBS` and `New Cybersecurity Jobs (N) – USAJOBS`.
  - Body (HTML + text): bullet list of new items with: **Job ID** – **Description (trimmed)** – **Direct Link**.
  - If **no** new jobs, do not send.
- **Front‑end** (`docs/`):
  - Pure static HTML/CSS/JS, responsive (mobile‑first). Two pages (`ai.html`, `cyber.html`) fetch respective JSON (`docs/data/*.json`) and render a searchable/sortable list (title, org, location, link). Keep JS tiny, no build tools. Ensure good a11y basics (labels, semantic tags).
- **Automation (GitHub Actions)**:
  - Trigger: `schedule` (daily, choose a sane UTC time) + `workflow_dispatch`.
  - Steps: checkout → setup python → install deps → run `python -m ai_cyberjobs.cli scrape --category ai` and `--category cyber` → run `python -m ai_cyberjobs.cli notify` (or use a mail action) → if there are file changes under `data/` and `docs/data/`, commit and push (configure `user.email` and `user.name` for bot). Use `if:` guards so email/commit only occur when new jobs exist.
  - Add caching for pip if trivial.
  - Set `permissions: contents: write`.
- **Quality**:
  - Lint with `ruff`, format with `black`, type‑check with `mypy` (strict enough to catch common issues), tests with `pytest` + coverage.
  - Pre‑commit hooks for ruff/black/mypy/pytest (fast checks) on commit.
  - `README.md` with quickstart, how to set secrets, how to run locally, and architecture diagram (ASCII ok).
  - `LICENSE` = MIT, add `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`.

IMPLEMENTATION PLAN (execute in order)
1) **Initialize new package**: create `pyproject.toml` (setuptools + PEP621), add dependencies:
   - runtime: `requests`, `pydantic`, `pydantic-settings`, `typer`, `python-dotenv` (if not using pydantic‑settings for .env), `tenacity` (retries)
   - dev: `ruff`, `black`, `mypy`, `pytest`, `pytest-cov`, `types-requests`, `pre-commit`
2) **Scaffold directories/files** exactly as in target structure (above).
3) **Migrate/Archive**: If useful CSV/JSON exist under `job_data/`, convert them to `data/history/*` (preserve), else delete `job_data/`. Remove all root‑level legacy `.py` files and tests that do not conform to the new layout.
4) **Config & models**:
   - Implement `config.py` with `Settings` reading from env + `.env` (path at repo root), strict types, defaults for non‑secret values.
   - Implement `models.py` (`Job`, `ResultSet`, etc.) with validation.
5) **USAJOBS client**:
   - Implement `client.base.JobsClient` protocol and `client.usajobs.USAJobsClient` with:
     - Proper auth headers (read from env). **Verify against current official USAJOBS API docs before finalizing.**
     - Query building that supports keyword search, posted/updated date filtering if available, paging, and rate limiting.
     - Robust error handling, retries (`tenacity`), and clear logging.
6) **Pipeline**:
   - `fetch.py`: orchestrate two category runs (“ai”, “cyber”).
   - `normalize.py`: map API results → `Job`, trim description, compute canonical `job_id`.
   - `dedupe.py`: compare to `data/state/known_*_ids.json` and return only new `Job` items.
   - `store.py`: write JSON/CSV for `data/latest/*.json` and also copy the two “latest” files to `docs/data/*.json`; append a dated snapshot `data/history/<category>/YYYY-MM-DD.json`. Ensure deterministic ordering (by posted date desc).
7) **Notifications**:
   - `notify/format.py`: render clean HTML + plain‑text bodies for a list of `Job`.
   - `notify/send.py`: if SMTP secrets exist, send two emails (AI and Cyber). If not present, log a clear message and exit with success (so CI doesn’t fail). Provide a CLI flag `--send/--no-send`.
8) **CLI (Typer)**:
   - Commands:
     - `scrape --category [ai|cyber|both] --days 2 --limit N --dry-run`
     - `notify --category [ai|cyber|both] --dry-run`
     - `build-site` (write/update `docs/data/*.json`; idempotent)
     - `validate` (quick sanity checks)
   - Ensure `python -m ai_cyberjobs.cli ...` works from repo root.
9) **Front‑end**:
   - Build `docs/index.html` with two big buttons/links (“AI Jobs”, “Cybersecurity Jobs”).
   - `docs/ai.html` and `docs/cyber.html` each load their JSON via `assets/app.js` and render a searchable, sortable list. Add basic responsive CSS in `assets/styles.css` (mobile‑first, readable font sizes/tap targets).
10) **GitHub Actions** (`.github/workflows/daily-scrape.yml`):
   - Runs daily on a chosen UTC cron (e.g., `0 12 * * *`) + `workflow_dispatch`.
   - Steps:
     - Checkout
     - Setup Python 3.11
     - Install deps
     - Run `scrape` for AI and Cyber (notifying how many new jobs)
     - If SMTP secrets are available: run `notify` (or use an SMTP send‑mail GitHub Action; consult its official docs and wire inputs from repo secrets).
     - If `data/` or `docs/data/` changed: configure git user, commit with message like `chore(data): update job feeds YYYY-MM-DD` and push using `GITHUB_TOKEN`. Guard with `git diff --quiet` to avoid empty commits.
   - Set `permissions: contents: write`.
11) **Quality tooling**:
   - `ruff`, `black`, `mypy` config in `pyproject.toml`.
   - `pre-commit` hooks: ruff check + black + mypy + quick pytest (or at least import check).
   - `Makefile` targets: `make install`, `make lint`, `make format`, `make typecheck`, `make test`, `make scrape-ai`, `make scrape-cyber`, `make site`.
12) **Docs & OSS hygiene**:
   - Rewrite `README.md` with: project overview, quickstart, env setup, how automation works, how to add keywords, how emails are sent, and how to enable GitHub Pages (serve `/docs`).
   - Add `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
13) **Verification**:
   - Local: `make install && make lint && make typecheck && make test`.
   - Dry run: `python -m ai_cyberjobs.cli scrape --category both --dry-run --limit 5` (prints counts, writes nothing).
   - Real run (if secrets present): `python -m ai_cyberjobs.cli scrape --category both && python -m ai_cyberjobs.cli notify --category both`.
   - Open `docs/ai.html` and `docs/cyber.html` locally (via simple file URL) to see tables render.

GITHUB PAGES NOTE
- Configure the repo to serve GitHub Pages from the `/docs` folder on the default branch. The workflow will keep `docs/data/*.json` current.

ASSUMPTIONS (encode in code comments where relevant)
- If USAJOBS “updated since” query is available, prefer it to reduce noise; otherwise use keyword search and dedupe by `job_id`.
- For **AI keywords**, start with: `["artificial intelligence","AI","machine learning","ML","deep learning","NLP","natural language processing","LLM","large language model","computer vision","generative","reinforcement learning"]`.
- For **Cybersecurity keywords**, start with: `["cybersecurity","information security","infosec","SOC","security analyst","threat","incident response","security engineer","penetration test","red team","blue team","SIEM"]`.
- Email recipients for both categories are **jdoner@ewu.edu** and **ssteiner@ewu.edu**.

ACCEPTANCE CRITERIA (do not stop until all are met)
[ ] Legacy `.py` files and `job_data/` are removed or migrated; new tree matches “TARGET PROJECT STRUCTURE”.
[ ] `ruff`, `black`, `mypy`, and `pytest -q` all pass locally (no type errors; tests include at least: client mapping/parsing, dedupe logic, store IO, notify formatting).
[ ] `python -m ai_cyberjobs.cli scrape --category both --limit 5 --dry-run` prints a sane summary without errors.
[ ] `docs/ai.html` and `docs/cyber.html` load their JSON and render readable, mobile‑friendly tables (local file open is sufficient).
[ ] `.github/workflows/daily-scrape.yml` exists, has `permissions: contents: write`, and uses `GITHUB_TOKEN` to push updates only when there are changes.
[ ] If SMTP secrets are present, `notify` sends two separate emails (AI and Cyber) with the required fields (job number, one‑paragraph description, direct link). If secrets not present, it skips sending gracefully.
[ ] A fresh contributor can follow `README.md` to run lint/tests locally and do a dry‑run scrape.
[ ] No secrets are committed; `.env.example` exists; `.gitignore` excludes `.env` and common artifacts.

OUTPUTS
- Fully working code and config committed to the repo.
- A short final summary in the chat describing:
  - What was deleted and why
  - What the new structure is
  - How to run locally and how the automation works
  - Any TODOs for the maintainer (e.g., setting repo secrets, enabling Pages)

BEGIN NOW
- Open a new branch `revamp/ai-cyber-scraper`.
- Implement the plan step‑by‑step with clear commits.
- Verify USAJOBS auth header names and search parameters from the latest official docs as you implement the client.
- Finish by pushing the branch and summarizing results with next steps.

Absolutely—we can push all emailing into **GitHub Actions** so you don’t touch SMTP code locally. You’ll still add a couple repo **secrets**, but the workflow will do the sending.

Below are (A) exactly what you need to do, and (B) minimal edits to your prompt so the agent implements this “email-via-Actions” design instead of Python SMTP.

---

## A) What you need to do

1. **Add repo secrets (GitHub → Settings → Secrets and variables → Actions):**

   * `USAJOBS_EMAIL` – the USAJOBS User-Agent email.
   * `USAJOBS_API_KEY` – the USAJOBS API key.
   * For email sending **by Actions** (pick one path):

     * **Office365/Outlook** *(works only if your school allows SMTP/app passwords)*

       * `SMTP_HOST` = `smtp.office365.com`
       * `SMTP_PORT` = `587`
       * `SMTP_USERNAME` = `jdoner@ewu.edu`
       * `SMTP_PASSWORD` = *app password or SMTP password*
       * `EMAIL_FROM` = `jdoner@ewu.edu`
     * **Gmail** *(usually the least friction—needs a Google “App Password”)*

       * `SMTP_HOST` = `smtp.gmail.com`
       * `SMTP_PORT` = `587`
       * `SMTP_USERNAME` = your Gmail address
       * `SMTP_PASSWORD` = Google **App Password**
       * `EMAIL_FROM` = that Gmail address
     * (Optional) If you prefer a transactional service instead of SMTP, you can swap the mail step for a SendGrid/Mailgun action later.

2. **Set GitHub Pages to serve `/docs`:**
   Settings → **Pages** → *Build and deployment*

   * **Source:** “Deploy from a branch”
   * **Branch:** your default branch (e.g., `main`)
   * **Folder:** `/docs`

3. **Ensure Actions can push data updates:**

   * In your workflow we’ll set `permissions: contents: write` and only commit when files changed.

---

## B) Minimal edits to your prompt (copy/paste replacements)

You don’t need to rewrite the whole thing. Just replace the indicated sections below.

### 1) Replace the **SECURITY & SECRETS** section with:

```text
SECURITY & SECRETS
- Do not commit `.env`. Add a `.env.example` and `.gitignore`.
- Use these secrets (read by GitHub Actions; the app itself does not send mail):
  - `USAJOBS_EMAIL` (User-Agent email required by USAJOBS)
  - `USAJOBS_API_KEY` (API key)
  - Email delivery (via GitHub Actions, not Python):
    - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`
      (These are repository **secrets** used only in the workflow’s mail step.)
- In GitHub Actions, set `permissions: contents: write` so the workflow can push data updates.
```

### 2) In **TARGET PROJECT STRUCTURE**, change the notify package to **render only** (no SMTP code):

```text
├── src/
│   └── ai_cyberjobs/
│       ...
│       ├── notify/
│       │   ├── format.py      # compose email bodies (HTML + text)
│       │   └── __init__.py
│       └── cli.py             # Typer CLI (scrape, notify --no-send only, build-site, validate)
└── tests/
    ...
    └── test_notify_format.py
```

*(i.e., remove `notify/send.py`)*

### 3) In **KEY DESIGN REQUIREMENTS → Emails**, change to:

```text
- Emails are sent by GitHub Actions, not by Python.
- CLI `notify` produces files (HTML + text) under `out/emails/`:
  - `ai.html`, `ai.txt`, `cyber.html`, `cyber.txt`
- Subjects:
  - AI:    "New AI Jobs (N) – USAJOBS"
  - Cyber: "New Cybersecurity Jobs (N) – USAJOBS"
- If no new jobs, do not produce email files and the workflow will skip sending.
```

### 4) In **IMPLEMENTATION PLAN → step 7 (Notifications)**, replace with:

```text
7) Notifications:
   - `notify/format.py`: render clean HTML + plain-text bodies for AI and Cyber lists.
   - `python -m ai_cyberjobs.cli notify --category both --no-send --output-dir out/emails`
     writes `out/emails/{ai,cyber}.{html,txt}` (idempotent).
```

### 5) In **IMPLEMENTATION PLAN → step 10 (GitHub Actions)**, replace with:

```text
10) GitHub Actions (`.github/workflows/daily-scrape.yml`):
   - Triggers: daily cron (UTC) + `workflow_dispatch`.
   - Steps:
     1) Checkout; setup Python 3.11; install deps.
     2) Run `scrape` for AI and Cyber (reads `USAJOBS_*` from secrets).
     3) Run `build-site` (updates `docs/data/*.json`).
     4) Detect changes; if none, exit successfully.
     5) Commit & push changes when present (configure bot identity).
     6) Run `notify --no-send --output-dir out/emails` to generate email files.
     7) Send **two emails** using an SMTP email GitHub Action:
        - Inputs (from secrets): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `EMAIL_FROM`.
        - To: `jdoner@ewu.edu, ssteiner@ewu.edu`
        - Subjects as specified; bodies from `out/emails/*.html` (fallback to `.txt` if needed).
```

### 6) In **ACCEPTANCE CRITERIA**, replace the email bullet with:

```text
[ ] The workflow sends two separate emails (AI and Cyber) *from GitHub Actions* using the generated HTML bodies when and only when new jobs exist (no changes → no email).
```

---

## C) Drop-in workflow you can keep in your prompt (and your repo)

Put this file at `.github/workflows/daily-scrape.yml` (the agent will create it, but you can keep this exact block in the prompt to be explicit):

```yaml
name: daily-scrape

on:
  schedule:
    - cron: "0 12 * * *"  # 12:00 UTC daily
  workflow_dispatch:

permissions:
  contents: write

jobs:
  run:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Scrape AI
        env:
          USAJOBS_EMAIL: ${{ secrets.USAJOBS_EMAIL }}
          USAJOBS_API_KEY: ${{ secrets.USAJOBS_API_KEY }}
        run: python -m ai_cyberjobs.cli scrape --category ai

      - name: Scrape Cyber
        env:
          USAJOBS_EMAIL: ${{ secrets.USAJOBS_EMAIL }}
          USAJOBS_API_KEY: ${{ secrets.USAJOBS_API_KEY }}
        run: python -m ai_cyberjobs.cli scrape --category cyber

      - name: Build site data
        run: python -m ai_cyberjobs.cli build-site

      - name: Detect changes
        id: changes
        run: |
          git add -A
          if git diff --cached --quiet; then
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "changed=true" >> $GITHUB_OUTPUT
          fi

      - name: Commit & push data/site updates
        if: steps.changes.outputs.changed == 'true'
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git commit -m "chore(data): update job feeds $(date -u +'%Y-%m-%d')"
          git push

      - name: Render email bodies (no send)
        if: steps.changes.outputs.changed == 'true'
        run: |
          python -m ai_cyberjobs.cli notify --category both --no-send --output-dir out/emails
          ls -la out/emails || true

      # === Email via SMTP action (works with Office365 or Gmail via secrets) ===
      - name: Send AI email
        if: steps.changes.outputs.changed == 'true'
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: ${{ secrets.SMTP_HOST }}
          server_port: ${{ secrets.SMTP_PORT }}
          username: ${{ secrets.SMTP_USERNAME }}
          password: ${{ secrets.SMTP_PASSWORD }}
          subject: New AI Jobs – USAJOBS
          to: jdoner@ewu.edu, ssteiner@ewu.edu
          from: ${{ secrets.EMAIL_FROM }}
          html_body: file://out/emails/ai.html
          ignore_cert: true

      - name: Send Cyber email
        if: steps.changes.outputs.changed == 'true'
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: ${{ secrets.SMTP_HOST }}
          server_port: ${{ secrets.SMTP_PORT }}
          username: ${{ secrets.SMTP_USERNAME }}
          password: ${{ secrets.SMTP_PASSWORD }}
          subject: New Cybersecurity Jobs – USAJOBS
          to: jdoner@ewu.edu, ssteiner@ewu.edu
          from: ${{ secrets.EMAIL_FROM }}
          html_body: file://out/emails/cyber.html
          ignore_cert: true
```

**How it behaves (exactly):**

* If nothing new was scraped → it **won’t** commit or email.
* If there are new jobs → it commits updated `data/*` and `docs/data/*`, renders `out/emails/*`, then sends two emails.

---

## D) Tiny wording tweak in your **GOAL #2**

Change:

> “Detects newly posted jobs and sends two separate emails …”

to:

> “Detects newly posted jobs and **uses GitHub Actions to send** two separate emails …”

That’s enough to keep the agent aligned with the “no local SMTP” approach.

---

### Optional aside (why this helps)

* Pushing email into Actions keeps secrets off your laptop and makes runs reproducible (classmates can fork and just add their own secrets).
* Keeping **notify = render-only** simplifies testing (you unit-test content, not SMTP).
* If EWU blocks SMTP, swapping to a service (SendGrid) is a one-line change in the workflow step rather than code surgery.

If you want, I can also give you a SendGrid-based mail step variant, but the above is ready to go now.
