# personal-website

Using Codex & Claude Code to create a personal website

## Setup

1. Clone the repository
2. Run setup: `make setup`
3. Edit `.env` with your configuration
4. Start the dashboard: `make dashboard`
5. Launch the command portfolio: `make flask-app`

## Development

- **Install dependencies**: `make install-dev`
- **Run tests**: `make test`
- **Lint code**: `make lint`
- **Format code**: `make format`
- **Clean artifacts**: `make clean`
- **Run Flask portfolio**: `make flask-app`

## Template Updates

If this project was created with cruft, you can update it when the template improves:

```bash
cruft update
```

## Project Structure

```
personal-website/
├── personal_website/     # Main package
├── tests/                               # Test files
├── personal_website/portfolio/          # Command-style portfolio (Flask)
├── .env.example                         # Environment template
├── pyproject.toml                       # Project configuration
└── Makefile                            # Development commands
```

## Requirements

- Python 3.12+
- UV package manager

## Command Portfolio App

The `personal_website.portfolio` package provides a terminal-inspired portfolio interface:

- Replace `personal_website/portfolio/static/files/demo_cv.pdf` with your actual resume for the `cv` command.
- Update command content or add new handlers in `personal_website/portfolio/commands.py`.
- Run locally with `make flask-app`, which wraps `uv run flask --app personal_website.portfolio.app run --debug`.
