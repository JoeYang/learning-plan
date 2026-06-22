"""Session-scoped state and the server-side PII vault.

Neither object is ever returned to the model. `SessionState` tracks tool-call
history that prerequisites depend on; `PIIVault` holds real customer records
that the model is never allowed to see directly.
"""

from dataclasses import dataclass, field
from typing import Optional
import secrets


@dataclass
class SessionState:
    """Tracks tool-call history within a single agent session.

    The model cannot inspect this — it only observes the structured returns
    from each tool call. State here is what makes prerequisites enforceable.
    """

    cached_customer_token: Optional[str] = None
    refunds_without_prerequisite: int = 0  # shadow audit; must stay 0


@dataclass
class PIIVault:
    """Server-side store mapping placeholder tokens to real customer records.

    Tools return tokens; real IDs / emails / cards never leave this object.
    Even if the agent's full output leaks, no PII goes with it.
    """

    _vault: dict[str, dict] = field(default_factory=dict)

    def store(self, real_record: dict) -> str:
        """Stash the real record privately; return a placeholder token."""
        token = f"cust_tok_{secrets.token_urlsafe(8)}"
        self._vault[token] = real_record
        return token

    def lookup(self, token: str) -> Optional[dict]:
        """Server-only resolver. Use to retrieve real IDs when actually
        charging a refund. Never expose the return value to the model."""
        return self._vault.get(token)
