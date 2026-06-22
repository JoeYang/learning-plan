"""Structured tool errors the model can reason about."""

from dataclasses import dataclass
from typing import Literal, Optional


ErrorType = Literal[
    "precondition_failed",
    "policy_violation",
    "not_found",
    "invalid_input",
    "rate_limit_exhausted",
    "upstream_error",
]


@dataclass(frozen=True)
class ToolError:
    """Returned from a tool when the call cannot succeed.

    The model receives this directly. Fields are designed so the model can
    decide its next action without guessing:

    - `error_type` — coarse category for branching
    - `is_retriable` — whether the same call could ever succeed
    - `next_action` — concrete tool/step to try next (optional)
    - `retry_after_seconds` — only when is_retriable and rate-limited
    - `message` — human-readable detail (also useful for logs)
    """

    error_type: ErrorType
    is_retriable: bool
    message: str
    next_action: Optional[str] = None
    retry_after_seconds: Optional[int] = None
