from __future__ import annotations

import uuid
from pathlib import Path

from flask import Flask, jsonify, request

from personal_website.config import config
from personal_website.logger import logger
from personal_website.portfolio.commands import CommandRegistry

PACKAGE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=str(PACKAGE_DIR / "templates"),
        static_folder=str(PACKAGE_DIR / "static"),
    )

    # Configure rate limiting
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        limiter = Limiter(
            get_remote_address,
            app=app,
            default_limits=[],
            storage_uri="memory://",
        )
    except ImportError:
        limiter = None
        logger.warning("flask-limiter not installed, rate limiting disabled")

    command_registry = CommandRegistry()

    @app.get("/")
    def index():
        return command_registry.render_index()

    @app.post("/command")
    def process_command():
        return command_registry.process_command()

    @app.post("/chat")
    def chat():
        """Handle chat mode messages with conversation history."""
        # Apply rate limiting if available
        if limiter:
            limiter.limit(f"{config.LLM_RATE_LIMIT_PER_MINUTE} per minute")(
                lambda: None
            )()

        payload = request.get_json(silent=True) or {}
        message = (payload.get("message") or "").strip()
        session_id = payload.get("session_id") or str(uuid.uuid4())

        if not message:
            return jsonify(
                {"kind": "error", "output": "Please enter a message.", "session_id": session_id}
            )

        try:
            from personal_website.portfolio.llm import get_llm_service

            llm = get_llm_service()
            response = llm.chat(session_id, message)
            return jsonify({"kind": "ai", "output": response, "session_id": session_id})
        except Exception as e:
            logger.error(f"Chat endpoint error: {e}")
            return jsonify(
                {
                    "kind": "error",
                    "output": "AI assistant is temporarily unavailable. Please try again.",
                    "session_id": session_id,
                }
            )

    @app.post("/chat/clear")
    def clear_chat():
        """Clear the chat session history."""
        payload = request.get_json(silent=True) or {}
        session_id = payload.get("session_id")

        if session_id:
            try:
                from personal_website.portfolio.llm import get_llm_service

                llm = get_llm_service()
                llm.clear_session(session_id)
            except Exception as e:
                logger.warning(f"Could not clear session: {e}")

        return jsonify({"kind": "success", "output": "Chat history cleared."})

    @app.get("/download/cv")
    def download_cv():
        cv_path = Path(app.static_folder) / "files" / "demo_cv.pdf"
        if not cv_path.exists():
            return command_registry.missing_cv_response()
        return command_registry.send_cv(cv_path)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(
            {
                "kind": "error",
                "output": "I need a moment to catch my breath. Please try again in a minute!",
            }
        ), 429

    return app


app = create_app()
