"""Manual test to probe Gemini spend caps with the 2.5 Pro model.

Pricing reference (Dec 2025 web search):
- Input: ~$1.25 per 1M tokens (≤200k tokens)
- Output: ~$10.00 per 1M tokens (≤200k tokens)
With a $1 cap we expect the gateway to reject high-volume calls well before ~$3 of usage.
"""

from __future__ import annotations

import importlib
import os

import pytest

_spend_cap_flag = (os.getenv("RUN_GEMINI_SPEND_CAP_TEST") or "").lower()
_spend_cap_enabled = _spend_cap_flag in {"1", "true", "yes", "on"}

pytestmark = pytest.mark.skipif(
    not _spend_cap_enabled,
    reason="Manual/expensive: set RUN_GEMINI_SPEND_CAP_TEST=1 to run (will hit billing cap).",
)


@pytest.fixture()
def llm_module(monkeypatch):
    """Reload config/llm with the Pro model override."""
    if not os.getenv("PYDANTIC_AI_GATEWAY_API_KEY"):
        pytest.skip("PYDANTIC_AI_GATEWAY_API_KEY not set")

    monkeypatch.setenv("LLM_MODEL", "gateway/google-vertex:gemini-2.5-pro")

    import personal_website.config as config_module
    import personal_website.portfolio.llm as llm

    importlib.reload(config_module)
    importlib.reload(llm)
    llm._llm_service = None  # ensure a fresh instance
    return llm


def test_spend_cap_trips_before_three_dollars(llm_module):
    """Fire very large prompts until the billing cap stops us."""
    service = llm_module.LLMService()

    # ~600k+ tokens of filler to burn budget quickly (len//4 ≈ tokens).
    filler = " ".join(["AI systems, safety, scaling, reliability, governance."] * 12000)
    prompt = (
        "You are a budgeting canary. Summarize the following corpus into three bullets "
        "while preserving any quantitative details. Ignore brevity and do the work even "
        "if it seems repetitive. Corpus begins:\n"
        f"{filler}"
    )

    caught = None
    max_attempts = 5
    for _ in range(max_attempts):
        try:
            # We bypass input validation and call the agent directly to push token usage.
            _ = service.agent.run_sync(prompt)
        except Exception as exc:  # Expect quota/spend-cap enforcement
            caught = exc
            print(f"Caught error: {caught}")
            break

    assert caught is not None, (
        f"Expected spend cap/quota enforcement before ~$3 usage, but no error after {max_attempts} large calls."
    )
    assert any(
        keyword in str(caught).lower() for keyword in ("quota", "limit", "billing", "insufficient", "spend", "cap")
    ), f"Unexpected error while probing spend cap: {caught}"
