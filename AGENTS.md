# Repository Guidelines

## Project Structure & Module Organization
- `personal_website/` holds the Streamlit app: `dashboard.py` drives the UI, `config.py` centralizes runtime settings, and `logger.py` configures Loguru logging.
- `tests/` mirrors the package and provides pytest suites such as `test_config.py`; add new tests alongside the module under test.
- Shared assets and configuration live at the repo root (`pyproject.toml`, `.env.example`, `Makefile`). Copy `.env.example` to `.env` before running the dashboard.

## Build, Test, and Development Commands
- `make setup` runs `uv sync --extra dev` and seeds `.env`; use it when onboarding or resetting dependencies.
- `make dashboard` launches the local Streamlit app via `uv run streamlit run personal_website/dashboard.py`.
- `make test`, `make lint`, and `make format` wrap pytest with coverage, Ruff lint, and Ruff formatter respectively.
- `make clean` purges caches such as `.pytest_cache` and `.ruff_cache`.

## Coding Style & Naming Conventions
- Target Python 3.12+ and keep line length ≤100 characters (Ruff enforces this from `pyproject.toml`).
- Prefer module-level functions in `personal_website/` for Streamlit sections; configure secrets through `config.py`.
- Use snake_case for functions and variables, PascalCase for classes, and keep Streamlit page identifiers descriptive (e.g., `render_financial_overview()`).
- Run `make format` before committing; Ruff handles both formatting and import sorting.

## Testing Guidelines
- Tests live in `tests/` and follow pytest’s `test_*.py` pattern; name test functions `test_<behavior>`.
- Ensure new features include coverage via `pytest --cov=personal_website --cov-report=term-missing` (run `make test`).
- Mock external services and environment variables via `monkeypatch` to keep the suite fast and deterministic.

## Commit & Pull Request Guidelines
- No shared git history is available; adopt a concise imperative subject (`feat: add dashboard section`) with optional details in the body.
- Group related changes per commit and mention associated issues (e.g., `Refs #42`) when relevant.
- Pull requests should: explain the change and motivation, list how to reproduce or verify (commands, screenshots of Streamlit views), and confirm `make test`/`make lint` were run locally.

## Configuration & Secrets
- Never commit `.env`; rely on `.env.example` for defaults and document new keys there.
- When adding settings, load via `dotenv` in `config.py` and thread them into `dashboard.py` through constructor parameters to simplify testing.
