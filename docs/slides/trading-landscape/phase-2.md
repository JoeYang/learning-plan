# Trading Landscape Phase 2 — Equities

Sessions 4–6: the audit side. What human equity traders watch, and how they read what the execution algos produced.

> **The theme:** cash equities are the most fragmented, most regulated, most intensively observed market in the world. A trader's job is not to run algorithms — it's to *read* what the algorithms did, catch anomalies, and escalate before the toxicity compounds.

---

## The problem Phase 2 solves

You know the math of TWAP, VWAP, and Implementation Shortfall from `trading-algos` Sessions 1–3. Phase 2 answers the other half of the question: **what does a human trader do with the output?**

- Stare at a live blotter all day, reading 30+ columns of data that update every second
- Decide when an algo is mis-behaving and needs to be re-parameterised, paused, or cancelled
- Read post-trade TCA reports to justify fills to portfolio managers and auditors
- Spot toxic flow before it eats the P&L

Equities is the perfect phase to learn these skills on — the tooling is mature, the regulations are explicit, and the tape is public.

---

## The venue landscape is not one market

The NYSE sticker price is a lie. A single US large-cap trades across **16+ lit exchanges**, **~30 dark pools**, and a handful of ATSs.

| Venue type | What it is | Why it exists |
|---|---|---|
| **Lit exchange** | Displayed quote book (NYSE, Nasdaq, IEX, CBOE) | Price discovery, retail flow, rebates |
| **Dark pool** | Non-displayed matching (Crossfinder, Liquidnet) | Institutional blocks without market impact |
| **ATS** | Alternative trading system, similar to dark | Broker-internal crossing, bespoke rules |
| **RFQ** | Request-for-quote (less common in US equities) | Blocks with named counterparties |

**Smart order routers (SORs)** pick between them per slice, factoring in:
- Rebate / fee per venue
- Recent fill quality (toxicity score)
- Latency to the venue
- Posted depth at that price

Fragmentation is **not** a bug. It's a direct consequence of Reg NMS (US) and MiFID II (EU) — regulations that force venues to compete for flow.

---

## SIP vs direct feeds — the latency arbitrage surface

Two ways to see the market:

| Feed | Who provides it | Latency | Cost | Use case |
|---|---|---|---|---|
| **SIP** (consolidated tape) | Exchange consortium | ~5–10 ms | Cheap | Retail, compliance, slow funds |
| **Direct feeds** | Each exchange separately | <1 ms | Expensive (hundreds of $k/year) | HFT, institutional execution |

The SIP-to-direct latency gap is the arbitrage surface HFT firms live on. If you quote off the SIP and someone hits you off the direct feed, you just sold at a price that moved 2ms ago.

Equity execution desks run on direct feeds. Retail brokers run on the SIP. Your algorithm's default feed choice is a material cost decision.

---

## What an equity trader watches

The blotter is the trader's world. A typical equity desk blotter has:

| Column | What it tells the trader |
|---|---|
| Symbol, side, size | The parent order basics |
| Arrival price, VWAP benchmark | What "good" looks like for this order |
| **Markouts @ 1s / 10s / 1m** | Post-fill price drift — toxicity signal |
| Fill rate vs schedule | Is the algo on pace? |
| Queue position at best | Am I at the front or the back of the book? |
| Live P&L (MtM and realised) | Portfolio-level heat |
| News feed ticker | Macro / micro events that could move the symbol |

The key signal most new traders miss: **markouts**. If you fill a buy at 100.00 and the mid drifts to 99.95 within 10 seconds, you've been picked off — that's adverse selection costing 5 cents per share, and it compounds.

---

## Implementation Shortfall — the audit view

`trading-algos` S2 derives the math. Phase 2 reads the report. An IS report decomposes the gap between **decision price** and **execution price** into three components:

```
IS = (execution - arrival) × shares
   = market impact   (permanent + temporary)
   + timing cost     (what the price did while we were working)
   + opportunity cost (missed fills, unfilled residual)
```

Every post-trade report answers three questions:
- **Did we pay the spread or earn it?** (market impact)
- **Did the market move against us?** (timing)
- **Did we miss fills we should have caught?** (opportunity)

A skilled equity trader reads the report, spots the dominant component, and tells the PM *why* the algo delivered what it did — not just that it did.

---

## Attribution tells — spotting what went wrong

Patterns that let you diagnose a report at a glance:

| Pattern in report | Likely cause |
|---|---|
| Small spread cost, big timing cost | Market moved — not the algo's fault, but maybe wrong urgency |
| Big spread cost, small timing cost | Algo too aggressive, or spread widened intra-day |
| Large opportunity cost (big residual unfilled) | Limit too tight, or volume forecast wrong |
| Negative markouts systematically | Adverse selection — venue or routing problem |
| Volume spike around your fill times | You signalled — predictability / leakage |

**Rule of thumb:** the report tells you *what* happened. The trader tells the PM *why*, and what to change next time.

---

## LULD and halts — when the tape breaks

**LULD** (Limit Up / Limit Down) — automatic 5-minute pauses when a stock moves more than a threshold (5%, 10%, 20% depending on band) within 5 minutes.

```
normal trading  →  LULD band breach  →  5 min auction pause  →  re-open via auction
```

For algos, halts are a discontinuity. Your VWAP schedule goes stale, your queue position resets, and you may miss the re-open if your algo wasn't built to handle it.

For humans, halts are the "go look at news" signal. Something material happened; the algorithm can't know what.

Other market-breaking events: circuit breakers (market-wide), trading halts (single-stock, non-LULD — news-driven), expiry-day close dynamics (triple/quadruple witching).

---

## Block trading — when the lit book won't work

For orders representing, say, 10%+ of ADV (average daily volume), the lit book is a trap. Posting there signals, and the price moves before you fill.

Options:
- **Dark pool match** — wait for a natural counterparty in a non-displayed venue
- **RFQ** — ask a handful of banks for a price on the block (more common in fixed income, but growing in equities)
- **Sunrise / close print** — use auction volume to absorb size
- **Worked over days** — slice aggressively over multiple sessions using IS

The block-vs-SOR decision is a trade-off between **impact** (lit route) and **information leakage** (dark / RFQ). Wrong call costs the PM real money.

---

## Phase 2 in one line

**Equities is the audit side.** You learn to read — not write — TCA reports, spot attribution tells, react to halts, and know when the lit book is the wrong answer for a block. The math was Phase 1 of `trading-algos`; Phase 2 here is the operational layer above it.

**Capstone:** `artefacts/trading-landscape/phase-2/equity-trader-dashboard.md` — mock the blotter, annotate each field.

Next phase: Futures — where margin, roll, and basis become the daily workflow.
