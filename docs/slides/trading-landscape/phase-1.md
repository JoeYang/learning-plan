# Trading Landscape Phase 1 — The ecosystem

Sessions 1–3: who does what, what trades, and the mechanics that span every asset.

> **The theme:** a trading algorithm only makes sense once you know whose decision it's automating, whose balance sheet it's moving, and whose policy gates it's subject to. Phase 1 is the map before the terrain — no depth per product yet.

---

## The problem Phase 1 solves

You can learn the math of TWAP, VWAP, Almgren-Chriss, Avellaneda-Stoikov — and still have no idea what a trader does for eight hours a day.

The gap is not conceptual; it's **operational context**. Every formula sits inside:

- A **role** (who is this algo serving?)
- A **flow** (where does an order start and end?)
- A **product** (what's the instrument, and how does it settle?)
- **Rules** (exchange, regulatory, internal risk)

Phase 1 surveys all four across five asset classes (equities, futures, options, FX, rates) so the phases that follow have somewhere to land.

---

## Sell-side vs buy-side

Two sides of every transaction. Know which one any role sits on.

| Side | Who | How they make money | Examples |
|---|---|---|---|
| **Sell-side** | Brokers, market makers, investment banks | Commission, spread, rebates, underwriting | Goldman Sachs, Citadel Securities, Virtu |
| **Buy-side** | Asset managers, hedge funds, pension funds | Management + performance fees on client capital | BlackRock, Bridgewater, AQR |

Rules of thumb:
- Sell-side serves **flow** — they exist because someone else wants to trade.
- Buy-side serves **capital** — they invest on behalf of end clients or LPs.
- A sell-side MM earns the spread on every round trip. A buy-side PM earns a fee on beating a benchmark.

---

## Four trader roles

Every trader you meet fits roughly one of these. The algorithm they use is a function of their role.

| Role | What they do | Primary pressure | Example algo |
|---|---|---|---|
| **Market maker** | Quote two-sided prices continuously, earn the spread | Inventory risk, adverse selection | Avellaneda-Stoikov |
| **Prop / speculator** | Take directional positions with own capital | Sizing, stop-loss, drawdown | Momentum, stat arb |
| **Execution / agency** | Fill a client's parent order with minimum impact | IS benchmark, best-ex | TWAP, VWAP, IS |
| **Hedger / risk** | Offset an existing exposure (portfolio, inventory, corporate) | Coverage ratio, basis risk | Delta hedging |

Same markets, same venues, different jobs. A single MM firm may run all four inside different desks.

---

## The flow lifecycle of one order

A parent order does not go from "decision" to "fill" in one step. It passes through hands — each of which can log, route, enrich, or reject it.

```
portfolio manager  →  trader  →  execution algo  →  broker / SOR
        (idea)        (sizing)       (slicing)       (routing)
                                                          ↓
                                               lit exchange or dark pool
                                                          ↓
                                                  matching engine (fill)
                                                          ↓
                                                    clearinghouse
                                                          ↓
                                           T+1 / T+2 settlement, custody
```

Joe's infrastructure work sits mostly between **execution algo → matching engine**: feed handlers, order gateways, risk checks, post-trade reporting. Everything above that hand-off is business logic; everything below it is market-structure plumbing.

---

## Five asset classes at a glance

| Class | What trades | Typical leverage | Settlement | Primary venue type |
|---|---|---|---|---|
| **Equities** | Shares in companies | 1× (margin 2–5×) | T+1 / T+2 | Continuous + opening/closing auctions |
| **Futures** | Standardised contracts on a reference price | 10–20× via margin | Daily MtM via CCP | Continuous |
| **Options** | Right (not obligation) to buy/sell at strike | Embedded (delta, gamma) | T+1, physical or cash | Continuous + auctions |
| **FX** | Exchange one currency for another | 20–100× via margin | T+2 (spot) | OTC with multiple ECNs |
| **Rates** | Lending/borrowing at a future rate | High (DV01-based) | T+1, varied | OTC + some exchange-listed |

Each class has its own microstructure, each trader role exists in every class, and every trading algorithm sits inside one of them.

---

## Order types — the cross-product toolkit

The same order types show up in every asset class. Know what each one promises and what it gives up.

| Type | Promises | Gives up |
|---|---|---|
| **Market** | Immediate fill | Price (pays the spread or worse) |
| **Limit** | Price (no worse than X) | Fill certainty |
| **IOC** (immediate-or-cancel) | No resting order on the book | Partial fills possible |
| **FOK** (fill-or-kill) | All-or-none immediate fill | Higher miss rate |
| **Post-only** | Only adds liquidity (earns rebate) | Rejected if it would cross |
| **Hidden / iceberg** | Visible size ≪ real size | Discoverable by refill patterns |
| **Stop / stop-limit** | Triggers at a price | May gap past in fast markets |

Picking the right order type per slice is where much of execution alpha lives — it's the same decision space TWAP/VWAP/IS algos automate.

---

## Venues, clearing, settlement

Where the fill actually happens, and what's left to do after.

**Venues** — where orders match:
- Lit exchanges (NYSE, Nasdaq, CME, LSE, ASX) — continuous matching + auctions
- Dark pools / ATSs — anonymous matching, typically for blocks
- RFQ networks — request-for-quote for illiquid products (bonds, swaps, structured)

**Auctions** — not always "continuous":
- Opening auction — single clearing price at market open
- Closing auction — single clearing price at market close (biggest print of the day)
- Unhalted / LULD auctions — re-opening after a volatility halt

**Clearing & settlement** — what happens after the fill:
- CCP (central counterparty) steps in between buyer and seller via **novation** — eliminates bilateral counterparty risk
- Variation margin flows daily (futures) or at settlement (equities)
- Final settlement — T+1 for most equities globally as of 2024, T+2 for FX spot, same-day for cleared swaps

The trader never sees most of this; it's plumbing. But when a CCP fails or variation margin spikes, your whole book cares.

---

## Pre-trade risk and P&L mechanics

Two things every trader's screen shows, constantly.

**Pre-trade risk** — the safety net that sits between the algo and the exchange:
- Position limits (per-symbol, per-book, per-desk)
- Notional checks (single-order and aggregate)
- Fat-finger checks (price deviation from mid, size anomaly)
- Kill switches (auto-pull quotes on vol spike, manual override)

**P&L** — two distinct numbers that don't match:
- **Mark-to-market P&L** — what the book is worth now at current mid
- **Realised P&L** — what you've actually crystallised in cash
- Plus: funding costs (repo, stock-loan borrow), exchange fees, maker rebates

Your MtM can be +$1M and your realised P&L zero. The difference is what you still have to unwind.

---

## Phase 1 in one line

**Before the math, the map.** Trading is a system of roles (sell-side vs buy-side × MM / prop / execution / hedger), an order lifecycle (PM → algo → venue → CCP → settlement), five asset classes with their own microstructure, and a shared toolkit of order types + risk checks + P&L mechanics.

**Capstone:** `artefacts/trading-landscape/phase-1/ecosystem-map.md` — one-page diagram of the ecosystem with your infrastructure work annotated onto it.

Next phase: Equities in depth — the audit side of what execution algos produce.
