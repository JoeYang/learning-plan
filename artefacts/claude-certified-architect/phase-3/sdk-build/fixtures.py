"""In-memory customer and order data for the build.

A real implementation would read from a CRM / order DB. For this artefact,
the focus is the tool-design patterns, not data plumbing.

Note the PII split:
- PII (real_customer_id, email, card_last4) — stays server-side; never
  returned by `get_customer`.
- Non-PII (tier, tenure_days, refund_quota_cents) — safe to surface to
  the model so it can reason about eligibility.
"""

CUSTOMERS: dict[str, dict] = {
    "cust_001": {
        "real_customer_id": "cust_001",        # PII — server-side only
        "email": "alice@example.com",          # PII — server-side only
        "card_last4": "4242",                  # PII — server-side only
        "tier": "gold",                        # non-PII
        "tenure_days": 845,                    # non-PII
        "refund_quota_cents": 200_000,         # non-PII
    },
    "cust_002": {
        "real_customer_id": "cust_002",
        "email": "bob@example.com",
        "card_last4": "1111",
        "tier": "silver",
        "tenure_days": 90,
        "refund_quota_cents": 50_000,
    },
}

# Lookup index used by `get_customer` (in real life this would be a DB query).
CUSTOMER_BY_EMAIL: dict[str, str] = {
    rec["email"]: cid for cid, rec in CUSTOMERS.items()
}

ORDERS: dict[str, dict] = {
    "ord_a1": {
        "order_id": "ord_a1",
        "real_customer_id": "cust_001",
        "amount_cents": 4_500,
        "status": "delivered",
    },
    "ord_a2": {
        "order_id": "ord_a2",
        "real_customer_id": "cust_001",
        "amount_cents": 75_000,  # above policy threshold — must escalate
        "status": "delivered",
    },
    "ord_b1": {
        "order_id": "ord_b1",
        "real_customer_id": "cust_002",
        "amount_cents": 1_200,
        "status": "shipped",
    },
}
