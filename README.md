# personal-website

A terminal-inspired personal portfolio built with Flask, developed with AI-assisted tooling (Codex & Claude Code).

Visitors interact with a command-line interface to explore my work, download my CV, and learn more about me.

## Quick Start

This project uses `uv` as the package manager. 

```bash
# Clone and setup
git clone <repo-url> && cd personal-website
# Assumes uv is installed
make setup

# Edit .env with your configuration
# Then run the portfolio
make run
```

Open [http://localhost:5000](http://localhost:5000) and type `help` to get started.
Prefer a quick summary? Visit [http://localhost:5000/summary](http://localhost:5000/summary).

## Requirements

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) package manager

## Development

| Command        | Description                        |
|----------------|-------------------------------------|
| `make setup`   | Install dev dependencies + seed `.env` |
| `make run`     | Run the Flask portfolio locally    |
| `make test`    | Run pytest with coverage           |
| `make lint`    | Check code with Ruff               |
| `make format`  | Auto-format with Ruff              |
| `make clean`   | Remove caches and build artifacts  |

## Customization

- **Bio**: Edit `_about_handler` in `personal_website/portfolio/commands.py`
- **CV**: Replace `personal_website/portfolio/static/files/cv.pdf` with your resume
- **Commands**: Add new handlers in `commands.py` and register them in `_register_default_commands()`

## TODO

- [x] Add test coverage
- [x] Add LLM chat integration
- [x] Deploy to hosting platform
