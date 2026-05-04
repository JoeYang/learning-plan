# Trading Landscape Phase 4 — Options

Sessions 11–14: payoffs, Greeks-as-a-trader-uses-them, implied vol, and options market making.

> **The theme:** an option is not a stock. It's a bet on *where* the underlying will be *and when*. The Greeks are how traders decompose that bet into separable, hedgeable risks. Phase 4 teaches you to read a book in terms of its Greeks, not its positions.

---

## The problem Phase 4 solves

Options traders don't think in "I'm long 100 shares of AAPL." They think in:
- "I'm long 0.3 delta on AAPL" — directional exposure
- "I'm long 0.02 gamma" — convexity
- "I'm short 0.05 theta" — bleeding $50/day in time decay
- "I'm long 10 vega" — $10 P&L per 1% move in implied vol

Each Greek isolates one risk. You can hedge them separately. And a professional options trader's screen shows *aggregated Greeks*, not individual positions.

This phase covers enough math to understand the Greeks, NO full Black-Scholes derivation. Put-call parity, yes. PDE derivation, no.

---

## Greek symbols — pronounce them and know what they mean in this phase

Every Greek you'll meet in this deck. Read aloud at least once.

| Symbol | Pronounce | Meaning in options |
|---|---|---|
| **δ** | *delta* | Rate of change of option price w.r.t. underlying: `∂V/∂S`. Directional exposure. |
| **γ** | *gamma* | Rate of change of delta w.r.t. underlying: `∂²V/∂S²`. Convexity. |
| **θ** | *theta* | Rate of change of option price w.r.t. time: `∂V/∂t`. Time decay (usually negative for long options). |
| **ρ** | *rho* | Rate of change w.r.t. interest rate: `∂V/∂r`. Usually small. |
| **σ** | *sigma* | Volatility of the underlying. Input to the model. |
| **vega** | *vega* (not Greek, named for the star) | Rate of change w.r.t. implied vol: `∂V/∂σ`. Core of a vol book. |

**Critical naming-collision callout:**

In Avellaneda-Stoikov (market making, `trading-algos` Phase 2), `γ` is a **preference parameter** — you *choose* how risk-averse to be.

In Black-Scholes (options, this phase), `γ` is a **measured quantity** — the convexity of the option's price, derived from the model.

Same letter, opposite epistemology. You CHOOSE Avellaneda γ. You COMPUTE Black-Scholes γ.

---

## Payoffs and put-call parity

Options have asymmetric payoffs — that's the whole point.

```
call payoff at expiry:   max(S_T - K, 0)
put payoff at expiry:    max(K - S_T, 0)
```

where `K` = strike, `S_T` = underlying at expiry.

**Put-call parity** relates calls, puts, and the underlying for European options on non-dividend stocks:

```
C - P = S - K · exp(-r · (T - t))
```

Intuition: holding a long call and short put (same K, same expiry) replicates being long stock financed at the risk-free rate. If prices deviate from parity, there's an arbitrage.

**Synthetic positions** — from parity:

```
synthetic long stock  =  long call + short put
synthetic short stock =  short call + long put
synthetic call        =  long stock + long put
synthetic put         =  short stock + long call
```

If you can't short the stock (hard-to-borrow), buying a synthetic via options can be cheaper.

---

## Greeks as a trader thinks — directional risks (δ, γ)

Not as calculus. As P&L exposures. The first two Greeks isolate your exposure to price moves.

### Delta — directional exposure

A delta of 0.3 means: if the underlying moves $1, this option's price moves $0.30.

**Use:** delta-hedging. Hold the option, sell 0.3 × (shares-per-contract) of the underlying. The net position is **delta-neutral** — first-order price-insensitive.

```
delta-hedged book:  Δ_portfolio ≈ 0
```

A long call has positive delta (0 to 1). A long put has negative delta (-1 to 0). ATM options have delta around ±0.5.

### Gamma — convexity

If delta changes when the underlying moves, you're **long gamma** (or short gamma).

- **Long gamma**: your hedge always lags the move. You buy more underlying as it falls, sell more as it rises. You profit on volatility.
- **Short gamma**: you sell into weakness, buy into strength. You lose on volatility.

```
long gamma  →  profit from realised vol > implied vol
short gamma →  profit from realised vol < implied vol
```

This is the fundamental bet of every options trader.

---

## Greeks as a trader thinks — time and vol (θ, vega)

Delta and gamma cover price moves. Theta and vega cover time decay and implied-vol sensitivity — the *cost* of holding options and the *independent bet* on the vol surface.

### Theta — time decay

Options lose value every day. Long options pay **theta rent**; short options collect it.

```
long option  →  θ < 0  (you bleed value daily)
short option →  θ > 0  (you earn decay)
```

**The gamma-theta tradeoff is everything:** you pay theta every day to stay long gamma. If realised vol doesn't exceed implied, you lose.

### Vega — vol sensitivity

If you're long an option, you're long vega — you profit when implied vol rises, lose when it falls.

**Vega traders** bet on the vol surface, not the underlying price. A short-dated earnings straddle might be long gamma AND long vega — two independent bets wrapped in one instrument.

---

## Implied volatility — the traded quantity

Black-Scholes takes volatility σ as an input. In practice, traders work it the other way:

```
observed option price  →  invert B-S  →  implied vol σ
```

**Implied vol is the tradable quantity.** Options traders quote in vol, not in price. The price is derived from the vol the market is pricing.

**Vol surface** — plot IV as a function of two axes:

| Axis | What moves it |
|---|---|
| **Strike / moneyness** | Skew (OTM puts richer than OTM calls — crash premium) |
| **Time to expiry** | Term structure (near-term vol vs far-term vol, event pricing) |

```
       IV
        |   * * * *  ← OTM puts rich (crash risk)
        | *         *
        *             *   ← OTM calls cheap (mostly)
        |_________________
            ATM       strike →
```

A "smile" says both tails are rich. A "smirk" says one tail dominates. The shape itself is tradable — skew trades, term-structure trades, vol-of-vol trades.

---

## Options market making — the operational layer

MMs in options don't quote price; they **quote vol**. They:

- Mark the current mid vol for each strike/expiry from the surface
- Compute theoretical option prices from that vol
- Quote bid/ask around the theoretical price, widened for inventory risk and adverse selection (same Avellaneda-Stoikov logic from `trading-algos`, adapted)
- Hedge each fill's delta immediately via the underlying (delta-hedge pipeline)
- Run a **vega book** — aggregate vol exposure across all strikes/expiries
- Run a **gamma book** — aggregate convexity exposure

Delta is hedged continuously. Gamma and vega are managed via offsetting option positions, not the underlying.

**Event risk** — around earnings, rate decisions, macro prints:
- Implied vol spikes in advance (event pricing)
- MMs widen spreads preemptively
- Some MMs pull quotes entirely on known events, resuming after the print

---

## Gamma-theta tradeoff — the fundamental equation of options trading

Every options position decomposes into:

```
daily P&L  ≈  ½ · γ · (ΔS)²  +  θ · Δt
              └─ realised vol ─┘    └ time decay ┘
```

- Long gamma, long theta cost: you need `(ΔS)²` to exceed the theta paid every day
- Short gamma, collect theta: you need `(ΔS)²` to stay below the theta earned

**The inequality every options trader cares about:**

```
realised vol  >  implied vol   →  long gamma wins
realised vol  <  implied vol   →  short gamma wins
```

All options strategies, from the simplest long-straddle to the most complex dispersion trade, are variants of betting on this inequality.

---

## Phase 4 in one line

**Options = payoffs + Greeks + implied vol.** Payoffs set the shape, Greeks decompose the risks, implied vol is the traded quantity. The γ naming collision is resolved: AS γ is preference, B-S γ is measurement. Every options trade is ultimately a bet on realised vol vs implied vol.

**Capstone:** `artefacts/trading-landscape/phase-4/vol-surface-annotated.md` + 5-day delta-hedging walk-through on a toy short-straddle book.

Next phase: FX and Rates — different beasts, carry-driven.
