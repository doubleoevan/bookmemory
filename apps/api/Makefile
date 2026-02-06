.PHONY: dev lint lint-fix format format-check typecheck check test run playwright

# install all dev dependencies
dev-setup: dev playwright

# install dev tooling (mypy, ruff, stubs, etc.)
dev:
	pip install -e .[dev]

# install Playwright browser for js extraction
playwright:
	python -m playwright install chromium

# format code and change files
format:
	ruff format .

# verify formatting without changing files
format-check:
	ruff format . --check

# lint without changing files
lint:
	ruff check .

# lint and change files
lint-fix:
	ruff check . --fix

# typecheck
typecheck:
	python -m mypy .

# validate without changing files
check: format-check lint typecheck

# run tests
test:
	pytest

# run the api locally
run:
	uvicorn bookmemory_api.main:app --reload
