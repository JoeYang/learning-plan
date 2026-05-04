# Trading Landscape Phase 3 — Futures

Sessions 7–10: contracts, margin, basis, term structure — the daily workflow of a futures trader.

> **The theme:** a future is not a stock. It's a time-stamped contract on an underlying reference price, and almost everything that makes futures interesting — leverage, basis, roll, term structure — flows from that one fact.

---

## The problem Phase 3 solves

Futures are where most real trading happens by volume — commodities, equity index, Treasury, FX, power. They're a trader's favourite instrument because:

- Leverage is built in (margin = 5–10% of notional, not the full amount)
- Mark-to-market is **daily** via the CCP, so P&L is visible and cash-settled in real time
- Liquidity concentrates into one front-month contract per product
- The yield curve (contango / backwardation) is itself a tradable signal

But: every future has an **expiry**, and the roll window is where most mistakes happen.

---

## Contract specs — what you need to read

Every futures contract has a spec sheet. Know these seven fields before trading anything.

| Field | Example (ES e-mini S&P 500) |
|---|---|
| **Underlying** | S&P 500 index |
| **Contract size / multiplier** | 50 × S&P index |
| **Tick size / value** | 0.25 = $12.50 |
| **Expiry months** | Mar / Jun / Sep / Dec (quarterly) |
| **Last trading day** | Third Friday of expiry month |
| **Settlement** | Cash-settled to special opening quotation |
| **Initial margin** | ~$12,000 per contract (varies, CME sets it) |

For commodity futures, add **delivery rules** — physical delivery is rare but mechanically possible, and impacts the last-day price.

**Initial margin** vs **variation margin**:
- Initial = deposit to open the position (locked up)
- Variation = daily flow of cash as the MtM changes (wins credited, losses debited)

A futures trader watches variation margin daily; it's the cash-flow P&L.

---

## The basis — spot vs futures

**Basis** = spot price − futures price.

For a non-dividend-paying asset, arbitrage-free pricing says:

```
F = S · exp(r · (T - t))
```

where:
- `F` = futures price
- `S` = spot price
- `r` = risk-free rate
- `T - t` = time to expiry

This is the **cost-of-carry** formula. In practice, basis reflects:

- Cost of financing the spot position (repo, stock-loan)
- Storage costs (commodities, livestock)
- **Convenience yield** (non-monetary benefit of holding the physical — huge for oil, power, agri)
- Dividends (subtract expected dividends for equity futures)

Basis is not constant — it moves with funding conditions, storage, and supply/demand for the physical. **Basis trades** exploit deviations from fair basis.

---

## Term structure — contango and backwardation

The **futures curve** plots price vs time-to-expiry across multiple contract months.

| Shape | Name | What it signals |
|---|---|---|
| Far-dated higher than front | **Contango** | Cost of carry > convenience yield (typical) |
| Far-dated lower than front | **Backwardation** | Convenience yield > carry (supply stress) |
| Flat | Neither | Equilibrium, unusual |

Classic example — oil:
- Normal market: slight contango (cost to store)
- Supply shock: deep backwardation (physical barrel in demand NOW)

**Roll yield** — the P&L you earn (or pay) simply by rolling a position from front to back month:

```
roll yield = (F_back - F_front) / F_front   per roll
```

- In contango, roll yield is **negative** — you roll up the curve, paying the carry
- In backwardation, roll yield is **positive** — you roll down the curve, earning the basis

For long-only commodity ETFs (USO, DBA), chronic contango is the silent tax that eats returns.

---

## Calendar spreads — the two-legged trade

A **calendar spread** is long one contract month + short another. You're not betting on the outright price; you're betting on the **shape of the curve**.

```
Jun/Sep calendar spread (long Jun, short Sep):
   profits if Jun outperforms Sep — steepening backwardation, or
   contango flattening
```

Calendar spreads have:
- **Lower margin** than outright positions (offsetting risk)
- **Lower outright price risk** — you're roughly delta-neutral to spot moves
- **Higher sensitivity to curve shape** — the whole point
- Their own order types on the exchange (traded as a single instrument)

Most futures MMs run calendar books alongside outrights. They're also how hedgers express views on supply timing.

---

## The roll window

Liquidity moves from the expiring contract to the next one over a window of 3–10 days before expiry. This is the **roll**.

```
volume (% of total):
                      _____________________
front-month _________/                    
                    /    ______________
back-month  _______/    /             
                       /
             roll-window starts        front-month expires
```

For a trader with a long-held position:
- Pick a day in the roll window to close front and open back
- Or spread the roll across multiple days to reduce impact
- Or use the exchange's **TAS** (Trade at Settlement) mechanism to roll at the settlement print

Getting roll timing wrong = paying extra basis. Large asset managers publish roll calendars (the "Goldman roll", "Bloomberg roll") that concentrate flow predictably — and faster traders front-run them.

---

## The futures trader's workflow

What a futures trader actually does, hour by hour:

| Time of day | Activity |
|---|---|
| Pre-open | Check overnight moves, macro events, CCP margin changes |
| Open | Watch opening-range volatility, place opening orders |
| Mid-session | Monitor positions, variation margin, basis vs fair value |
| **Roll window** | Execute rolls (or delegate to roll algo), watch front/back volume shift |
| Close / settlement | Settlement print prices all outstanding contracts for margin |
| Post-close | Review P&L, basis, roll cost, prep for next day |

**Evaluation metrics:**
- Carry P&L (earned or paid) — separate from price moves
- Roll cost (what did the roll actually cost vs mid-curve?)
- Basis exposure (did the hedge match the underlying? any leakage?)

---

## Phase 3 in one line

**Futures = contract + expiry + margin + basis.** Almost every futures-specific decision (calendar spreads, roll timing, term-structure trades) is a play on one of those four. The math is simpler than options; the operational care required is higher because expiry is a real, hard deadline.

**Capstone:** `artefacts/trading-landscape/phase-3/basis-and-roll-memo.md` — 2-page memo decomposing a concrete ES or CL roll.

Next phase: Options — where the Greeks show up, and the γ naming collision with `trading-algos` Avellaneda-Stoikov finally gets resolved.
