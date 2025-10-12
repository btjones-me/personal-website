.PHONY: install install-dev lint format test clean dashboard flask-app setup

# Development commands
install:
	uv sync

install-dev:
	uv sync --extra dev

lint:
	uv run --extra dev ruff check .

format:
	uv run --extra dev ruff format .

test:
	uv run --extra dev pytest

# Application commands
dashboard:
	uv run streamlit run personal_website/dashboard.py

flask-app:
	uv run flask --app personal_website.portfolio.app run --debug

# Setup commands
setup: install-dev
	@echo "Setting up personal-website..."
	@if [ ! -f .env ]; then cp .env.example .env && sed -i '/^#/d' .env; echo "Created .env file from template"; fi
	@echo "Setup complete! Edit .env with your configuration, then run 'make dashboard'"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
