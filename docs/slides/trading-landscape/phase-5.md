# Trading Landscape Phase 5 — FX and Rates

Sessions 15–18: FX mechanics and workflow, rates mechanics and workflow. Two curve-driven markets, one phase.

> **The theme:** both FX and rates are fundamentally about **interest rate differentials across time**. FX trades the spot rate plus the forward curve; rates trades the yield curve directly. Neither is about "up or down" — both are about *where* and *when*.

---

## The problem Phase 5 solves

You've covered equities (vertical slices) and futures/options (time-stamped contracts). FX and rates are different:

- **FX** is 24-hour, OTC, over ECNs and voice. No single exchange. Notional at ~$7.5T/day (BIS triennial 2022).
- **Rates** are global, deeply liquid in Treasuries and swaps, priced off a curve rather than a single number.

Both are dominated by central bank policy, carry trades, and cross-currency funding. And both have their own Greek-letter-free math: DV01, duration, convexity.

This phase covers enough mechanics to understand the workflows. Depth comes from practice.

---

## FX products — the stack

Four instruments, one market.

| Product | Mechanics | Settlement | Use |
|---|---|---|---|
| **Spot** | Exchange now at the spot rate | T+2 | Actual FX conversion |
| **Forward** | Exchange at a future date, rate fixed now | T+N (weeks to years) | Hedging, speculation |
| **Swap** | Spot + reverse forward, packaged | N/A (combined) | Rolling forwards, funding |
| **NDF** | Non-deliverable forward — cash-settles in USD, no actual FX | T+settlement date | Currencies with capital controls (INR, BRL, KRW) |

**Covered interest parity** — no-arbitrage relationship:

```
F / S  =  (1 + r_foreign)  /  (1 + r_domestic)
```

Given spot S, and interest rates for the two currencies, the fair forward F is determined. Any deviation is an arbitrage — in practice, enforced by FX swap markets.

---

## The carry trade — FX's signature strategy

**Idea:** borrow in a low-rate currency, lend in a high-rate currency, pocket the rate differential.

Classic example (historical):
- Borrow JPY at 0%
- Convert to AUD at spot
- Buy AUD government bonds yielding 4%
- Carry = 4% per year

**The catch:** covered interest parity says the forward FX rate should exactly offset the carry. So uncovered (unhedged) carry only wins if FX moves *less* than the forward predicts.

Carry works, on average, over long periods. But it has **negative skew** — lots of small wins, occasional giant losses when the funding currency rallies hard (USD strength in 2008, JPY in 2024).

**The carry trader's watchlist:**
- Central bank meetings (rate changes = carry changes)
- Risk-off signals (VIX spikes, equity sell-offs — carry unwinds violently)
- Funding stress (LIBOR-OIS spreads, cross-currency basis)

---

## FX trader workflow — 24 hours in three sessions

FX doesn't sleep. Liquidity migrates.

```
Tokyo open     →     London open     →     NY open     →     NY close
  (22:00 UTC)       (07:00 UTC)           (13:00 UTC)       (21:00 UTC)
```

- **Tokyo** dominates JPY pairs; thin liquidity elsewhere
- **London** is the deepest session (40%+ of daily volume); London fix at 16:00 LDN is a huge print
- **NY** takes over; Fed data releases, equity open spill over
- **Close** — typically lowest liquidity, holidays magnify

**Fixings** — reference rates computed daily or intraday:
- **WMR / London 4pm fix** — the most-watched benchmark, used for index rebalancing
- CME's EBS reference rates
- Central bank fixings (ECB reference rates)

Huge volume hits the tape in the minutes before and after the fix as asset managers rebalance. It's also a known manipulation surface (multi-bank fines, 2013–2015).

---

## Rates — the yield curve as a tradable object

Rates markets price interest across time. Core instruments:

| Instrument | What it trades | Curve used |
|---|---|---|
| **Treasuries** | Government debt, cash settle | Treasury curve |
| **STIR futures** | Short-term interest rate (SOFR futures, Euribor) | Short end of curve |
| **Swaps** | Fixed-for-floating exchange | Swap curve (OIS-based post-LIBOR) |
| **Swaptions** | Options on swaps | Vol surface over swap curve |
| **Basis swaps** | Floating-for-floating across tenors / currencies | Spread between curves |

**The yield curve** plots yield vs tenor:

```
   yield
     |      ______________
     |     /                  ← long end (10y, 30y)
     |    /
     |   /                    ← belly (2y, 5y)
     |  /
     | /                      ← short end (O/N, 1y)
     |_________________________
       0    2    5   10   30   tenor (years)
```

Shape signals:
- **Steep**: market expects rising rates (economic expansion)
- **Flat**: late cycle, Fed pausing
- **Inverted**: recession signal (short rates > long rates)

---

## DV01 — the rates equivalent of delta

**DV01** = **D**ollar **V**alue of one basis **01** — how many dollars you gain (or lose) if yields drop by 1bp.

```
DV01 ≈ duration · price · 0.0001
```

For a 10-year Treasury at par:
- Duration ≈ 9 years
- Price = 100
- DV01 ≈ 9 × 100 × 0.0001 = $0.09 per $100 face
- Scale to $10M face: DV01 ≈ $9,000

Every rates position is sized by DV01, not by face amount. A steepener (long 2y, short 10y) is set up to be **DV01-neutral** at the belly — the bet is curve shape, not outright rates.

**Convexity** — the second derivative. Duration changes as yields change. Convexity matters for large moves and long-dated bonds.

---

## Rates trader workflow — curves, not prices

A rates trader's blotter shows:

| Field | What it means |
|---|---|
| Symbol, tenor | 2y, 5y, 10y, 30y — the tenor is part of the identity |
| DV01 | Per-position sensitivity |
| Butterfly / steepener P&L | Shape trades decomposed |
| Repo rate | Financing cost for the position |
| Curve regime (steepening/flattening) | Current shape dynamics |
| Macro event calendar | CPI, NFP, FOMC meetings — binary risk |

**Common trades:**
- **Steepener**: long short-end, short long-end (DV01-neutral) — bet on curve steepening
- **Flattener**: short short-end, long long-end — bet on flattening
- **Butterfly**: long 2y + long 10y, short 5y — bet on belly richening/cheapening vs wings
- **Basis**: on-the-run vs off-the-run, bond vs swap

**Evaluation:**
- DV01-neutral P&L (strip out outright rate moves)
- Carry + roll-down (the P&L you earn just holding the position)
- Convexity contribution on large moves

---

## OIS / SOFR transition — post-LIBOR reality

For decades, swaps and floating-rate products referenced **LIBOR**. LIBOR was manipulated (2012+), and regulators killed it.

Replacement:
- USD: **SOFR** (Secured Overnight Financing Rate, based on Treasury repo)
- EUR: **€STR**
- GBP: **SONIA**
- JPY: **TONA**

Key differences:
- SOFR is backward-looking (observed); LIBOR was forward-looking (surveyed)
- SOFR is near-risk-free (Treasury-collateralised); LIBOR had bank credit risk
- Swap conventions changed: spreads tighter, basis trades emerged (LIBOR legacy vs SOFR)

The transition is 95%+ done. Lingering LIBOR legacy contracts are running off. New trades are SOFR-native.

---

## Phase 5 in one line

**FX and rates are curve-driven markets.** FX is a 24-hour global spot-plus-forward market driven by interest rate differentials; rates trades the yield curve directly. Both are DV01-sized (for rates) or carry-sized (for FX), both are central-bank-driven, both have distinct workflows from equities or options.

**Capstone:** `artefacts/trading-landscape/phase-5/carry-and-curve-trade.md` — one FX carry trade + one rates steepener, each with sizing, risk, kill criteria.

Next phase: Market making across products — bringing the operational lens back over every asset class covered so far.
