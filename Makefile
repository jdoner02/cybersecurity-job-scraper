PY=python3
PIP=pip

.PHONY: install lint format typecheck test precommit site scrape-ai scrape-cyber

install:
	$(PIP) install -e .[dev]
	pre-commit install

lint:
	ruff check src tests

format:
	ruff check --fix src tests || true
	black src tests

typecheck:
	mypy src tests

test:
	pytest -q

scrape-ai:
	$(PY) -m ai_cyberjobs.cli scrape --category ai

scrape-cyber:
	$(PY) -m ai_cyberjobs.cli scrape --category cyber

site:
	$(PY) -m ai_cyberjobs.cli build-site

