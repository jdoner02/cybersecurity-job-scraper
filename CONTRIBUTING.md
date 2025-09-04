# Contributing

Thanks for your interest in contributing! This project aims to provide a clean, reliable pipeline that scrapes USAJOBS for AI and Cybersecurity roles, publishes data and a small static site, and automates email notifications via GitHub Actions.

## Getting started

- Python 3.11+
- `make install` to set up dev dependencies and pre-commit hooks
- Copy `examples/.env.example` to `.env` and fill in values as needed

## Development workflow

- Run `make format && make lint && make typecheck && make test` before opening a PR
- For quick local checks: `python -m ai_cyberjobs.cli scrape --category both --dry-run --limit 5`

## Code style

- Follow type hints and keep functions small and testable
- Use `ruff` and `black` per the configured settings

## Security

- Never commit secrets. Use `.env` locally and repository secrets in GitHub Actions.

