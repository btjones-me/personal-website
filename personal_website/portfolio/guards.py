"""Input sanitization and rate limiting guards for LLM endpoints."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Patterns that suggest prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"forget\s+(all\s+)?(previous|prior|above)",
    r"system\s*prompt",
    r"you\s+are\s+now",
    r"act\s+as\s+(if\s+you\s+are|a)",
    r"pretend\s+(to\s+be|you\s+are)",
    r"new\s+instructions",
    r"override\s+(instructions|rules)",
    r"<\s*system\s*>",
    r"\[\s*system\s*\]",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    error_message: str | None = None


def validate_input(message: str, max_chars: int = 500) -> ValidationResult:
    """Validate user input for safety and length constraints.

    Args:
        message: The user's input message
        max_chars: Maximum allowed character length

    Returns:
        ValidationResult with is_valid=True if safe, or error details if not
    """
    if not message or not message.strip():
        return ValidationResult(is_valid=False, error_message="Message cannot be empty.")

    message = message.strip()

    # Check length
    if len(message) > max_chars:
        return ValidationResult(
            is_valid=False,
            error_message=f"Message too long. Please keep it under {max_chars} characters.",
        )

    # Check for prompt injection patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(message):
            return ValidationResult(
                is_valid=False,
                error_message="I can only answer questions about Ben's professional background.",
            )

    # Check for excessive repetition (potential token stuffing)
    words = message.lower().split()
    if len(words) > 5:
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        max_repetition = max(word_counts.values())
        if max_repetition > len(words) * 0.5:  # More than 50% same word
            return ValidationResult(
                is_valid=False,
                error_message="Please ask a clear question about Ben's experience.",
            )

    return ValidationResult(is_valid=True)


def sanitize_output(response: str, max_chars: int = 1500) -> str:
    """Sanitize LLM output before returning to user.

    Args:
        response: The LLM's response
        max_chars: Maximum allowed output length

    Returns:
        Sanitized response string
    """
    if not response:
        return "I couldn't generate a response. Please try again."

    # Truncate if too long
    if len(response) > max_chars:
        response = response[:max_chars].rsplit(" ", 1)[0] + "..."

    return response.strip()

