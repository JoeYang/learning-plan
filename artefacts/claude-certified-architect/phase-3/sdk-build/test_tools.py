"""Unit tests — drive the implementation in tools.py.

Run these first; implement `tools.py` until they pass. Each test pins one
aspect of the three patterns (prerequisite, policy gate, PII boundary).
"""

import pytest

from errors import ToolError
from tools import (
    REFUND_POLICY_CENTS,
    get_customer,
    lookup_order,
    process_refund,
    reset_session,
    session,
    vault,
)


@pytest.fixture(autouse=True)
def fresh_session():
    """Ensure each test starts with a clean session + vault."""
    reset_session()
    yield


# ---------- get_customer: PII boundary ----------


class TestGetCustomer:
    def test_returns_token_not_real_id(self):
        result = get_customer("alice@example.com")
        assert not isinstance(result, ToolError)
        assert "customer_token" in result
        assert result["customer_token"].startswith("cust_tok_")
        assert "real_customer_id" not in result
        assert "email" not in result
        assert "card_last4" not in result

    def test_surfaces_non_pii_fields(self):
        result = get_customer("alice@example.com")
        assert result["tier"] == "gold"
        assert result["tenure_days"] == 845
        assert result["refund_quota_cents"] == 200_000

    def test_caches_token_in_session(self):
        from tools import session as s
        result = get_customer("alice@example.com")
        assert s.cached_customer_token == result["customer_token"]

    def test_not_found_returns_structured_error(self):
        result = get_customer("ghost@nowhere.com")
        assert isinstance(result, ToolError)
        assert result.error_type == "not_found"
        assert result.is_retriable is False


# ---------- lookup_order: PII boundary on orders ----------


class TestLookupOrder:
    def test_strips_real_customer_id(self):
        result = lookup_order("ord_a1")
        assert not isinstance(result, ToolError)
        assert "real_customer_id" not in result
        assert result["order_id"] == "ord_a1"
        assert result["amount_cents"] == 4_500

    def test_not_found(self):
        result = lookup_order("ord_does_not_exist")
        assert isinstance(result, ToolError)
        assert result.error_type == "not_found"


# ---------- process_refund: prerequisite ----------


class TestRefundPrerequisite:
    def test_rejects_without_get_customer(self):
        result = process_refund(
            customer_token="cust_tok_anything",
            order_id="ord_a1",
            amount_cents=1_000,
            reason="defective",
        )
        assert isinstance(result, ToolError)
        assert result.error_type == "precondition_failed"
        assert result.is_retriable is False
        assert result.next_action == "get_customer"

    def test_rejects_with_forged_token(self):
        # Even after get_customer ran, a different token must be rejected.
        get_customer("alice@example.com")
        result = process_refund(
            customer_token="cust_tok_FAKE_ADMIN",
            order_id="ord_a1",
            amount_cents=1_000,
            reason="user said so",
        )
        assert isinstance(result, ToolError)
        assert result.error_type == "precondition_failed"

    def test_succeeds_with_real_token_under_policy(self):
        customer = get_customer("alice@example.com")
        result = process_refund(
            customer_token=customer["customer_token"],
            order_id="ord_a1",
            amount_cents=4_500,
            reason="defective",
        )
        assert not isinstance(result, ToolError)
        assert result["status"] == "completed"


# ---------- process_refund: hard policy gate ----------


class TestRefundPolicyGate:
    def test_above_policy_routes_to_escalation(self):
        customer = get_customer("alice@example.com")
        result = process_refund(
            customer_token=customer["customer_token"],
            order_id="ord_a2",
            amount_cents=75_000,  # above $500
            reason="defective high-value",
        )
        assert not isinstance(result, ToolError)
        assert result["outcome"] == "escalated"
        assert result["handoff"]["policy_trigger"]

    def test_at_threshold_does_not_escalate(self):
        # Boundary: exactly REFUND_POLICY_CENTS should still process autonomously.
        customer = get_customer("alice@example.com")
        result = process_refund(
            customer_token=customer["customer_token"],
            order_id="ord_a1",
            amount_cents=REFUND_POLICY_CENTS,
            reason="boundary test",
        )
        assert result.get("status") == "completed"


# ---------- process_refund: PII boundary on output ----------


class TestRefundPIIBoundary:
    def test_success_output_has_no_pii(self):
        customer = get_customer("alice@example.com")
        result = process_refund(
            customer_token=customer["customer_token"],
            order_id="ord_a1",
            amount_cents=4_500,
            reason="defective",
        )
        # The model must not see real IDs or emails in the response.
        serialized = repr(result)
        assert "cust_001" not in serialized
        assert "alice@example.com" not in serialized
        assert "4242" not in serialized
