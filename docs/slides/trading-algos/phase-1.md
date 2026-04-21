# Trading Algos Phase 1 — Execution Algorithms

Sessions 1–3: you have a parent order to execute. How do you slice it?

> **The theme:** execution is a **scheduling problem**, not a prediction problem. Pick a benchmark, pick an urgency, accept the tradeoff between market impact (trading fast) and timing risk (trading slow).

---

## The parent-order problem

You're given **Q** shares to buy or sell over time **T**. The market doesn't want to fill all of **Q** right now — large prints move price.

Two forces pull in opposite directions:

- **Trade fast →** pay temporary and permanent market impact.
- **Trade slow →** expose yourself to adverse price drift (timing risk).

Every execution algorithm is a different answer to: **how do you split Q over T?**

---

## TWAP — trade on the clock

Time-Weighted Average Price. The simplest schedule:

```
qᵢ = Q / N
```

Trade equal slices at equal intervals. Benchmark is the average price over **[0, T]**.

- **When to use:** low urgency, no volume signal, thin markets where volume profile is unreliable.
- **Strength:** trivially simple, transparent, robust to bad volume forecasts.
- **Weakness:** predictable — adversaries can front-run a timer-driven child-order stream.

Implementation note: timing wheels give O(1) insert/cancel for many concurrent timers.

---

## VWAP — trade with the volume

Volume-Weighted Average Price. Slice proportional to expected volume:

```
qᵢ = Q · (V̂ᵢ / V̂)
```

Volume profile is the historical intraday **U-shape** — heavy at open and close, light midday.

- **Benchmark:** the day's VWAP, a widely accepted execution quality metric.
- **Strength:** dominates TWAP in liquid markets where volume is forecastable.
- **Weakness:** garbage-in if the forecast is wrong (earnings day, news).

Production pattern: volume-driven pacemaker that opportunistically toggles between passive (earn spread) and aggressive (cross spread) within each window.

---

## Implementation shortfall — the real benchmark

**Slippage between decision price and actual execution price.** Measures what the portfolio manager cares about, not what the trader games.

IS decomposes into:

- **Temporary impact** `η · v` — spread + book depletion, recovers after the trade.
- **Permanent impact** `γ · v` — information leakage, doesn't recover.
- **Timing risk** `σ² · τ` — price drift while you're still working the order.

VWAP minimises tracking error to a volume benchmark. IS minimises **expected cost** against decision price. Different objectives, different optimal schedules.

---

## Almgren–Chriss — the closed form

Minimise a risk-adjusted cost:

```
min  E[Cost] + λ · Var[Cost]
```

Euler–Lagrange → ODE `ẍ = κ²x` with `κ = √(λσ²/η)`.

Solution:

```
x(t) = Q · sinh(κ(T − t)) / sinh(κT)
```

- **κ → 0** (risk-neutral): recovers TWAP.
- **κ → ∞** (very risk-averse): immediate execution.
- **λ** is the dial: trader picks a point on the efficient frontier.

κ is the **urgency parameter** — high vol → high κ → front-load execution.

---

## The efficient frontier of execution

Plot expected cost vs variance of cost. Every λ traces out a Pareto-optimal curve.

- **Low λ:** patient, low expected cost, high variance (TWAP-like).
- **High λ:** aggressive, higher expected cost, low variance (front-loaded).

No schedule is "best" in absolute terms — you pick a point based on how much timing risk you can stomach.

The **limit vs market** decision inside each slice is where real execution alpha lives: behind schedule + volatile + tight spread → market; ahead of schedule + calm + wide spread → limit.

---

## POV and Iceberg — the rest of the toolkit

**POV (Percentage of Volume):** trade at a fixed fraction of observed volume.

```
qᵢ = ρ · Vᵢ_observed
```

- **When to use:** you want to *be* a consistent share of flow, not hit a schedule.
- **Risk:** in a volume surge, your child orders scale proportionally — no natural cap.

**Iceberg / reserve orders:** show a small visible size, refill from a hidden reserve on execution.

- **Use:** conceal large resting size from the book.
- **Detection:** predictable refill patterns, identical visible sizes, and time-to-refill fingerprints give icebergs away.

---

## The comparison table

| Algo | Optimises | Inputs | Predictability | Complexity |
|---|---|---|---|---|
| **TWAP** | Time-averaged price | Q, T | High | Low |
| **VWAP** | Volume-weighted price | Q, T, volume profile | Medium | Medium |
| **IS / Almgren–Chriss** | Expected cost vs variance | Q, T, σ, η, γ, λ | Low | High |
| **POV** | Participation rate | Q, ρ | Medium (reactive) | Low |
| **Iceberg** | Concealment | Q, visible size | Depends on detection | Low |

Choose by **what you're being measured on** — the benchmark dictates the algorithm.

---

## Phase 1 in one line

**Execution is scheduling under the impact–risk tradeoff.** TWAP and VWAP pick the schedule *ex ante*; IS/Almgren–Chriss derives it from the tradeoff itself; POV and Iceberg are reactive overlays.

Next phase: Market Making — the other side of the trade, where you *post* liquidity instead of consuming it.
