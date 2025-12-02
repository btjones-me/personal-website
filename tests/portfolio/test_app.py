from __future__ import annotations

import pytest

import personal_website.portfolio.app as app_module
from personal_website.portfolio.app import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index_renders_portfolio_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"command-driven portfolio" in response.data


def test_help_command_lists_available_commands(client):
    response = client.post("/command", json={"command": "help"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["kind"] == "text"
    for command_name in ("help", "about", "cv", "clear"):
        assert command_name in data["output"]


def test_unknown_command_returns_error(client):
    response = client.post("/command", json={"command": "foobar"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["kind"] in {"ai", "error"}
    assert isinstance(data.get("output"), str) and data["output"]
    if data["kind"] == "error":
        # If the LLM fallback is unavailable, we fall back to a static error.
        assert data["output"] == (
            "We seem to be having a bit of trouble on our end - sorry about that. Try 'help' to see available commands."
        )

def test_unix_command_hint(client):
    response = client.post("/command", json={"command": "ls -la"})
    data = response.get_json()
    assert response.status_code == 200
    assert data == {
        "kind": "error",
        "output": "Oops sorry, this is just a simulation of a real terminal. Type 'help' to see available commands.",
    }


def test_empty_command_prompts_for_input(client):
    response = client.post("/command", json={"command": "   "})
    data = response.get_json()
    assert response.status_code == 200
    assert data == {"kind": "error", "output": "Type a command to get started."}


def test_cv_command_provides_download_response(client):
    response = client.post("/command", json={"command": "cv"})
    data = response.get_json()
    assert response.status_code == 200
    assert data == {
        "kind": "download",
        "output": "Opening CV download in a new tab...",
        "url": "/download/cv",
    }


def test_download_cv_serves_file_attachment(client):
    response = client.get("/download/cv")
    assert response.status_code == 200
    content_disposition = response.headers.get("Content-Disposition", "")
    assert content_disposition.startswith("attachment;")
    assert "benjamin_jones_cv.pdf" in content_disposition


def test_download_cv_missing_file_returns_error(monkeypatch):
    monkeypatch.setattr(app_module.Path, "exists", lambda self: False)
    app = create_app()
    app.config.update({"TESTING": True})
    client = app.test_client()

    response = client.get("/download/cv")
    data = response.get_json()
    assert response.status_code == 200
    assert data == {
        "kind": "error",
        "output": "CV file missing. Replace 'static/files/demo_cv.pdf' with your actual resume.",
    }
