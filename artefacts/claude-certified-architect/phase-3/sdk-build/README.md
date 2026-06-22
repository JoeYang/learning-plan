# SDK Build A — Programmatic Prerequisites & PII Boundaries

Capstone for Session 12 of Claude Certified Architect Phase 3.

## What this proves

Three safety properties are enforced in **tool code**, not in the system prompt.
The model cannot bypass them — even under adversarial prompts — because the checks
live in `tools.py`, where prompt manipulation cannot reach.

| Invariant | Enforced by |
|---|---|
| `process_refund` only succeeds after `get_customer` runs in the same session | Prereq check in `process_refund` |
| Refunds > $500 unconditionally route to `escalate_to_human` | Hard policy gate in `process_refund` |
| Real customer IDs and emails never appear in tool outputs | `PIIVault` — tools return placeholder tokens |

## Files

| File | Purpose |
|---|---|
| `tools.py` | The three tools — main learning artefact |
| `errors.py` | `ToolError` dataclass for structured failures |
| `state.py` | `SessionState` + `PIIVault` (server-side, never returned to model) |
| `fixtures.py` | In-memory customers and orders |
| `test_tools.py` | Unit tests for each pattern (run these first to drive the build) |
| `test_adversarial.py` | 10 adversarial calls, asserts bypass counter == 0 |
| `adversarial-test-log.md` | Captured output of the adversarial run |

## Running

```bash
uv run pytest -v
```

## Build order (TDD)

1. Read `test_tools.py` and `test_adversarial.py` — the assertions define the contract.
2. Implement `errors.py` → `state.py` → `fixtures.py` (data shapes).
3. Implement `tools.py` against the tests until both files pass.
4. Capture the adversarial test output into `adversarial-test-log.md`.

## Why this matters for the exam

Mock 1 Scenario 1 scored 3/10. The recurring exam trap: prompt rules and model
judgement crumble under adversarial input. Only **tool-layer enforcement** holds.
This build turns the principle *"intelligence in the model, enforcement in tools"*
into muscle memory.

## Out of scope for this build

- Real MCP transport (stdio/SSE). Tools are plain Python functions with
  MCP-style contracts; wiring into an `mcp` server is mechanical and orthogonal
  to the patterns being learned.
- Real refund execution. The tool returns a success record; no money moves.
- Agent-driven adversarial test (prompts → Claude → tool calls). Tool-layer
  testing is sufficient to prove the enforcement boundary; agent-loop testing
  is the next step in Session 14.
