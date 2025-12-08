from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List
import re

from flask import Response, jsonify, render_template, request, send_file, url_for

from personal_website.logger import logger


@dataclass(frozen=True)
class Command:
    name: str
    description: str
    handler: Callable[[str], Dict[str, str]]


class CommandRegistry:
    """Encapsulates command definitions and bridge functions for Flask routes."""

    _SIMULATED_TERMINAL_MESSAGE = (
        "Oops sorry, this is just a simulation of a real terminal. Type 'help' to see available commands."
    )

    _UNIX_COMMANDS = (
        "ls",
        "cd",
        "rm",
        "pwd",
        "cat",
        "touch",
        "mkdir",
        "rmdir",
        "cp",
        "mv",
        "chmod",
        "chown",
        "find",
        "grep",
        "head",
        "tail",
        "less",
        "more",
        "ps",
        "top",
        "kill",
    )
    _UNIX_PATTERN = re.compile(rf"^\s*({'|'.join(_UNIX_COMMANDS)})\b", re.IGNORECASE)

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._llm_enabled = True
        self._summary_commands = ("about", "contact", "cv")
        self._register_default_commands()

    # --- Flask integration helpers -------------------------------------------------
    def render_index(self) -> str:
        return render_template("index.html")

    def process_command(self) -> Response:
        payload = request.get_json(silent=True) or {}
        raw_command: str = (payload.get("command") or "").strip()
        if not raw_command:
            return jsonify({"kind": "error", "output": "Type a command to get started."})

        if self._is_unix_command(raw_command):
            return jsonify(
                {
                    "kind": "error",
                    "output": self._SIMULATED_TERMINAL_MESSAGE,
                }
            )

        command_name, *args = raw_command.split(maxsplit=1)
        command = self._commands.get(command_name.lower())

        if command:
            result = command.handler(raw_command)
            return jsonify(result)

        # Unknown command - try LLM fallback if enabled
        if self._llm_enabled:
            return self._handle_llm_fallback(raw_command)

        return jsonify(
            {
                "kind": "error",
                "output": f"Unknown command: '{command_name}'. Type 'help' to see options.",
            }
        )

    def _handle_llm_fallback(self, question: str) -> Response:
        """Handle unknown commands by forwarding to LLM as questions."""
        try:
            from personal_website.portfolio.llm import get_llm_service

            llm = get_llm_service()
            response = llm.ask(question)
            return jsonify({"kind": "ai", "output": response})
        except Exception as e:
            logger.error(f"LLM fallback error: {e}")
            return jsonify(
                {
                    "kind": "error",
                    "output": "AI assistant is unavailable. Type 'help' to see available commands.",
                }
            )

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
        self.register(
            Command(
                name="contact",
                description="Get my contact details and social links.",
                handler=self._contact_handler,
            )
        )
        self.register(
            Command(
                name="chat",
                description="Enter AI chat mode for a conversation about Ben.",
                handler=self._chat_handler,
            )
        )
        self.register(
            Command(
                name="exit",
                description="Exit AI chat mode and return to commands.",
                handler=self._exit_handler,
            )
        )

    def register(self, command: Command) -> None:
        self._commands[command.name.lower()] = command

    # --- Command handlers ----------------------------------------------------------
    def _help_handler(self, _: str) -> Dict[str, str]:
        commands_help = "\n".join(
            self._format_command_line(cmd) for cmd in self._commands.values()
        )
        banner = (
            "Available commands (type them just like you would in a terminal):\n"
            f"{commands_help}\n\n"
            "💡 Tip: You can also just ask me questions directly!"
        )
        return {"kind": "text", "output": banner}

    def _about_handler(self, _: str) -> Dict[str, str]:
        about_sections: List[str] = [
            """Hi there. My name's Ben, and I currently head up AI & Machine Learning at Motorway, leading teams that build applied AI products powering the UK's fastest-growing used vehicle marketplace. My work sits at the intersection of AI, product, and engineering — turning complex machine learning and AI into reliable, safe, and commercially impactful solutions.

In addition to my day job, I advise startups on AI, ML, and data science strategy — helping them design, build, and operationalise intelligent systems, and have spoken at a number of conferences including as a main stage speaker at Google Cloud's London Summit in 2024 and Big Data London in 2025.

Before Motorway, I led ML at computer vision startup DeGould and worked as a technical consultant for 4 years across Accenture, Anglo American, and the UK's Ministry of Defence. My consulting experiences allowed me to hone my ability to spot commercial opportunity — and I take pride in ensuring every AI initiative is grounded in adding real business or user value. 

With a hands-on foundation in data science and ML engineering, my focus more recently has been on delivering transformational experiences with agentic generative AI systems. I'm passionate about building high-performing teams and creating ethical, scalable AI systems that drive real impact.

Want to know more? Just ask a question here, and my assistant will do its best to help!""",
        ]
        return {"kind": "text", "output": "\n\n".join(about_sections)}

    def _cv_handler(self, _: str) -> Dict[str, str]:
        download_url = url_for("download_cv")
        return {
            "kind": "download",
            "output": "",
            "url": download_url,
        }

    def _clear_handler(self, _: str) -> Dict[str, str]:
        return {"kind": "clear", "output": ""}

    def _contact_handler(self, _: str) -> Dict[str, str]:
        contact_info = """Get in touch:

  Email     btjones.me+contact@gmail.com
  GitHub    https://github.com/btjones-me
  LinkedIn  https://www.linkedin.com/in/benthomasjones/"""
        return {"kind": "text", "output": contact_info}

    def _chat_handler(self, _: str) -> Dict[str, str]:
        return {
            "kind": "chat_start",
            "output": (
                "🤖 Entering chat mode! Ask me anything about Ben's experience, "
                "skills, or background. Type 'exit' or 'end' to return to command mode, "
                "or 'help' to see chat tips."
            ),
        }

    def _exit_handler(self, _: str) -> Dict[str, str]:
        return {
            "kind": "chat_end",
            "output": "Exited chat mode. Type 'help' to see available commands.",
        }

    # --- Utility helpers -----------------------------------------------------------
    def _format_command_line(self, command: Command) -> str:
        return f"  {command.name:<8} {command.description}"

    def list_commands(self) -> Iterable[Command]:
        return self._commands.values()

    def _is_unix_command(self, raw_command: str) -> bool:
        """Detect common Unix commands to nudge users toward the simulated commands."""
        return bool(self._UNIX_PATTERN.match(raw_command))

    def get_summary_sections(self) -> List[Dict[str, Any]]:
        """Return a list of commands to surface in the summary view."""
        sections: List[Dict[str, Any]] = []
        for name in self._summary_commands:
            command = self._commands.get(name)
            if not command:
                continue

            payload = command.handler(command.name)

            sections.append(
                {
                    "name": command.name,
                    "title": command.name.title(),
                    "description": command.description,
                    "payload": payload,
                }
            )

        return sections
