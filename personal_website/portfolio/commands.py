from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List

from flask import Response, jsonify, render_template, request, send_file, url_for


@dataclass(frozen=True)
class Command:
    name: str
    description: str
    handler: Callable[[str], Dict[str, str]]


class CommandRegistry:
    """Encapsulates command definitions and bridge functions for Flask routes."""

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._register_default_commands()

    # --- Flask integration helpers -------------------------------------------------
    def render_index(self) -> str:
        return render_template("index.html")

    def process_command(self) -> Response:
        payload = request.get_json(silent=True) or {}
        raw_command: str = (payload.get("command") or "").strip()
        if not raw_command:
            return jsonify({"kind": "error", "output": "Type a command to get started."})

        command_name, *_ = raw_command.split(maxsplit=1)
        command = self._commands.get(command_name.lower())
        if not command:
            return jsonify(
                {
                    "kind": "error",
                    "output": f"Unknown command: '{command_name}'. Type 'help' to see options.",
                }
            )

        result = command.handler(raw_command)
        return jsonify(result)

    def send_cv(self, cv_path: Path) -> Response:
        return send_file(cv_path, as_attachment=True, download_name="benjamin_jones_cv.pdf")

    def missing_cv_response(self) -> Response:
        return jsonify(
            {
                "kind": "error",
                "output": (
                    "CV file missing. Replace 'static/files/demo_cv.pdf' with your actual resume."
                ),
            }
        )

    # --- Command definitions -------------------------------------------------------
    def _register_default_commands(self) -> None:
        self.register(
            Command(
                name="help",
                description="List all available commands and what they do.",
                handler=self._help_handler,
            )
        )
        self.register(
            Command(
                name="about",
                description="Read a short introduction about me.",
                handler=self._about_handler,
            )
        )
        self.register(
            Command(
                name="cv",
                description="Download my current CV as a PDF.",
                handler=self._cv_handler,
            )
        )
        self.register(
            Command(
                name="clear",
                description="Clear the virtual terminal history.",
                handler=self._clear_handler,
            )
        )

    def register(self, command: Command) -> None:
        self._commands[command.name.lower()] = command

    # --- Command handlers ----------------------------------------------------------
    def _help_handler(self, _: str) -> Dict[str, str]:
        commands_help = "\n".join(self._format_command_line(cmd) for cmd in self._commands.values())
        banner = (
            "Available commands (type them just like you would in a terminal):\n"
            f"{commands_help}"
        )
        return {"kind": "text", "output": banner}

    def _about_handler(self, _: str) -> Dict[str, str]:
        about_sections: List[str] = [
            "Hi, I'm Benjamin Jones — a software engineer who loves crafting thoughtful "
            "developer experiences and human-friendly tooling.",
            "I specialize in full-stack product work with a focus on Python, cloud-native "
            "platforms, and low-friction automation. Lately I've been exploring ways to infuse "
            "AI assistance into day-to-day workflows.",
            "When I'm not shipping features, you'll likely find me experimenting with sourdough "
            "recipes, sketching design ideas, or mentoring folks who are new to tech.",
        ]
        return {"kind": "text", "output": "\n\n".join(about_sections)}

    def _cv_handler(self, _: str) -> Dict[str, str]:
        download_url = url_for("download_cv")
        return {
            "kind": "download",
            "output": "Opening CV download in a new tab...",
            "url": download_url,
        }

    def _clear_handler(self, _: str) -> Dict[str, str]:
        return {"kind": "clear", "output": ""}

    # --- Utility helpers -----------------------------------------------------------
    def _format_command_line(self, command: Command) -> str:
        return f"  {command.name:<8} {command.description}"

    def list_commands(self) -> Iterable[Command]:
        return self._commands.values()
