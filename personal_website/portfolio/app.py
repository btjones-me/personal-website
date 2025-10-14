from __future__ import annotations

from pathlib import Path

from flask import Flask

from personal_website.portfolio.commands import CommandRegistry

PACKAGE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(PACKAGE_DIR / "templates"),
        static_folder=str(PACKAGE_DIR / "static"),
    )

    command_registry = CommandRegistry()

    @app.get("/")
    def index():
        return command_registry.render_index()

    @app.post("/command")
    def process_command():
        return command_registry.process_command()

    @app.get("/download/cv")
    def download_cv():
        cv_path = Path(app.static_folder) / "files" / "demo_cv.pdf"
        if not cv_path.exists():
            return command_registry.missing_cv_response()
        return command_registry.send_cv(cv_path)

    return app


app = create_app()
