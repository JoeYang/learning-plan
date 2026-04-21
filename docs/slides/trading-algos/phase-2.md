# Trading Algos Phase 2 — Market Making

Sessions 4–7: how liquidity providers think, price, and survive.

> **The theme:** a market maker's job is to quote a two-sided price and **not get run over**. The math is about compensating for two things — inventory risk and adverse selection — then adjusting for everything the textbook doesn't cover.

---

## The market maker's core problem

You continuously post a bid and an ask around some mid-price **s**.

- **Revenue:** the spread, earned when both sides fill on round trips.
- **Cost 1 — inventory risk:** every unfilled side leaves you holding **q** units exposed to price drift.
- **Cost 2 — adverse selection:** informed traders pick off your stale quotes when the mid moves against you.

Spread must cover both costs, or you lose money slowly and then all at once.

---

## The Roll decomposition

Roll (1984) showed the spread itself encodes the cost structure:

$$\text{Cov}(\Delta P_t, \Delta P_{t-1}) = -c^2$$

where **c** is the effective half-spread. Negative autocovariance in trade-to-trade price changes comes from **bid-ask bounce** — consecutive trades alternate sides of the spread.

- Gives you an **implicit** spread estimate from trade prices alone, no quote data needed.
- Decomposes spread into: order-processing cost + inventory cost + adverse-selection cost.

---

## Avellaneda–Stoikov — the setup

Continuous time, horizon **T**, mid-price follows Brownian motion:

$$dS_t = \sigma \, dW_t$$

- Inventory **q**, risk aversion **γ**, volatility **σ**, time remaining **(T − t)**.
- Order arrivals are Poisson with intensity **λ(δ) = A·e^(−κδ)** — the further you quote from mid, the less likely you fill.
- Maximise expected exponential utility of terminal wealth → HJB equation → closed-form quotes.

---

## Avellaneda–Stoikov — reservation price

The price at which you're **indifferent** to holding the current inventory:

$$r(s, q, t) = s - q \cdot \gamma \cdot \sigma^2 \cdot (T - t)$$

- **q > 0 (long):** reservation price is below mid — you'd rather sell, so shade quotes down.
- **q < 0 (short):** reservation price is above mid — shade quotes up.
- Scales with **γσ²(T−t):** more risk aversion, more volatility, more time left → more aggressive shading.

The reservation price is where you **centre** the spread, not mid.

---

## Avellaneda–Stoikov — optimal spread

Total quoted spread around **r**:

$$\delta^* = \gamma \sigma^2 (T - t) + \frac{2}{\gamma} \ln\!\left(1 + \frac{\gamma}{\kappa}\right)$$

Two distinct compensation terms:

| Term | Compensates for | Grows with |
|---|---|---|
| **γσ²(T − t)** | Inventory risk | Risk aversion, vol, time horizon |
| **(2/γ) · ln(1 + γ/κ)** | Adverse selection | Low κ (fill intensity insensitive to price) |

Bid = r − δ*/2, Ask = r + δ*/2. Quotes are **asymmetric around mid** whenever q ≠ 0.

---

## Skewing in practice

The textbook reservation-price shift is fine in theory. In production, market makers **skew quotes** more pragmatically:

- **Long inventory:** lower **both** bid and ask → encourage sells, discourage buys.
- **Short inventory:** raise **both** → encourage buys, discourage sells.
- Skew size is usually **nonlinear** in q — small near zero, steep near position limits.

Guéant–Lehalle–Fernandez-Tapia (2012) gives closed-form extensions with exponential utility and hard inventory bounds.

---

## What the textbook misses

Real books break the Avellaneda–Stoikov assumptions. The fixes:

- **Discrete tick sizes** → you can't quote at r ± δ*/2; you round and deal with the residual.
- **Queue position** → being first at a price level is alpha; FIFO queues reward patience.
- **Make/take fees** → maker rebates can flip the sign of a marginal trade's P&L.
- **Toxic flow detection** → large aggressive orders, cross-venue moves, correlated-instrument leads all signal that your quote is about to be picked off.

The model tells you **where** to quote. Microstructure tells you **whether to be there at all**.

---

## When market making works — and doesn't

| Regime | MM outcome |
|---|---|
| Range-bound, high volume, tight spreads | Works — spread capture dominates adverse selection |
| Trending markets | Fails — inventory accumulates against the trend |
| News events | Fails — adverse selection spikes faster than you can widen |
| Low liquidity, wide spreads | Ambiguous — wider spread helps, but fills are sparse |

Rule of thumb: **widen on uncertainty, pull on conviction.** A market maker who won't cancel won't survive.

---

## Phase 2 in one line

**Spread = inventory risk + adverse selection.** The model gives you the centre and width; practice tells you when to step out of the market entirely.

Capstone (Session 7): comparison table — Avellaneda–Stoikov vs Guéant–Lehalle–Fernandez-Tapia vs practical skewing, with when each applies and what breaks them.
