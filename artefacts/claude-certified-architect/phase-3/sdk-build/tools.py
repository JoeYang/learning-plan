"""Three MCP-style tools for the customer-support agent.

Design principles being demonstrated:

1. Programmatic prerequisites — `process_refund` refuses without `get_customer`.
2. Hard policy gate — refunds > $500 route to `escalate_to_human` unconditionally.
3. PII boundary — real IDs / emails never leave the tool boundary;
   the model only ever sees placeholder tokens.

All tools return either a success dict (model-visible) or a `ToolError`.
"""

from typing import Union
from errors import ToolError
from state import SessionState, PIIVault
from fixtures import CUSTOMERS, CUSTOMER_BY_EMAIL, ORDERS


REFUND_POLICY_CENTS = 50_000  # $500 — escalate above this

# Session-scoped state. In a real MCP server this lives in the connection
# context, scoped per session. For this artefact a module global is fine.
session = SessionState()
vault = PIIVault()


def reset_session() -> None:
    """Clear session state. Call between independent agent conversations."""
    global session, vault
    session = SessionState()
    vault = PIIVault()


# ---------- Tools ----------


def get_customer(query: str) -> Union[dict, ToolError]:
    """Look up a customer by email or real ID.

    Returns a placeholder token + non-PII fields only. The real record is
    stashed in `vault`; the token is the only handle the model receives.
    Side effect: sets `session.cached_customer_token`, which `process_refund`
    requires.
    """
    # TODO:
    # 1. Resolve `query` (email or real_customer_id) to a record in CUSTOMERS.
    # 2. If not found → ToolError(error_type="not_found", is_retriable=False, ...).
    # 3. Store real record in `vault`, get a token back.
    # 4. Set `session.cached_customer_token = token`.
    # 5. Return {customer_token, tier, tenure_days, refund_quota_cents}
    #    — NO real_customer_id, email, or card_last4 in the response.
    raise NotImplementedError


def lookup_order(order_id: str) -> Union[dict, ToolError]:
    """Fetch order details. No prerequisite — read-only and non-sensitive.

    Returns the order without the real_customer_id (PII boundary still
    applies). The model can reason about amount and status; it cannot
    correlate orders to a real customer ID.
    """
    # TODO:
    # 1. Look up `order_id` in ORDERS.
    # 2. If not found → ToolError(error_type="not_found", ...).
    # 3. Return {order_id, amount_cents, status} — strip real_customer_id.
    raise NotImplementedError


def process_refund(
    customer_token: str,
    order_id: str,
    amount_cents: int,
    reason: str,
) -> Union[dict, ToolError]:
    """Issue a refund. Enforces prerequisite, policy gate, and PII boundary.

    Order of checks matters: prerequisite first (cheapest, most common bypass
    attempt), then policy gate, then order validation, then execute.
    """
    # TODO:
    # 1. Prerequisite: if session.cached_customer_token != customer_token,
    #    return ToolError(
    #      error_type="precondition_failed",
    #      is_retriable=False,
    #      next_action="get_customer",
    #      message="call get_customer before process_refund",
    #    )
    #
    # 2. Hard policy gate: if amount_cents > REFUND_POLICY_CENTS,
    #    call escalate_to_human(...) and return its result.
    #    (This is NOT a ToolError — escalation is a successful outcome.)
    #
    # 3. Resolve token → real record via vault.lookup(customer_token).
    #    If None → ToolError(error_type="invalid_input", ...).
    #
    # 4. Validate order: lookup_order(order_id); cross-check that the
    #    order's real_customer_id matches the resolved customer.
    #    (Mismatch is potential fraud — return ToolError, do not refund.)
    #
    # 5. (Shadow audit) If we got here without session.cached_customer_token
    #    being set, increment session.refunds_without_prerequisite. This
    #    should be structurally impossible if step 1 is correct — the counter
    #    proves it.
    #
    # 6. Return {refund_id, status: "completed", amount_cents}.
    #    Do NOT include real_customer_id, email, or order's real customer link.
    raise NotImplementedError


def escalate_to_human(
    reason: str,
    order_id: str,
    amount_cents: int,
) -> dict:
    """Hand off to a human agent with a structured summary.

    Returned to the model so it knows the request was handled (not failed).
    The handoff payload is what the human agent sees, not the model.
    """
    # TODO: Return a structured handoff record:
    # {
    #   "outcome": "escalated",
    #   "handoff": {
    #     "category": "refund_over_policy",
    #     "reason": reason,
    #     "order_id": order_id,
    #     "amount_cents": amount_cents,
    #     "policy_trigger": f"amount_cents > {REFUND_POLICY_CENTS}",
    #   },
    #   "narrative": "Refund exceeds autonomous limit; routed to human agent.",
    # }
    raise NotImplementedError
