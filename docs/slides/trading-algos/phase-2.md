# Trading Algos Phase 2 — Market Making

Sessions 4–7: how a market maker thinks about profit, risk, and quoting.

> **The theme:** a market maker is **not** a speculator. They don't predict direction — they rent out their balance sheet as a counterparty and charge a spread for the service. Every formula in this phase answers one question: **how do you price that service so it stays profitable?**

---

## The problem — what is a market maker trying to do?

**Goal:** make money by being the counterparty to other people's trades.

You post a **bid** (I'll buy at 99.98) and an **ask** (I'll sell at 100.02) simultaneously. If both fill, you've bought at 99.98 and sold at 100.02 — **4¢ profit with no view on direction**.

- You don't forecast.
- You don't bet on up or down.
- You collect a toll every time both sides of your quote fill.

The spread is the toll. Everything else in this phase is about keeping the toll profitable.

---

## The challenge — two ways to lose money

### 1. Inventory risk

Someone buys from you at 100.02. You're now short 1 share. Before anyone hits your bid at 99.98, the mid drifts up to 100.10.

You're underwater 8¢ on the short — the 2¢ you earned is gone and you're still exposed.

**The longer you hold inventory, the more the market can move against you.**

### 2. Adverse selection

The people who trade with you tend to be the ones who can hurt you.

An informed trader hits your ask at 100.02 because they **know** the price is going to 100.10. They're not random flow — they're picking you off because your quote is stale.

**Your quote is an option. Informed traders exercise it against you.**

---

## Greek symbols — pronounce them, know what they mean

Before the formulas, the cast of characters. All lowercase unless noted.

| Symbol | Pronounce | Meaning in this phase |
|---|---|---|
| **γ** | *gamma* | Risk aversion — how much the MM dislikes variance. Higher γ → tighter inventory control, wider spread |
| **σ** | *sigma* | Volatility of the mid-price. Higher σ → wider spread, faster inventory punishment |
| **σ²** | *sigma squared* | Variance (σ × σ). Appears because risk scales with variance, not std dev |
| **κ** | *kappa* | Order-arrival intensity decay. How quickly fills drop off as you quote further from mid. Small κ → flow is insensitive to your price (bad — you're being picked off) |
| **δ** | *delta* | Quoted spread (total width). `δ*` means "optimal δ" |
| **λ** | *lambda* | Poisson arrival rate of orders (appears inside κ's definition) |
| **q** | *(latin)* | Inventory — net position. Positive = long, negative = short |
| **s** | *(latin)* | Mid-price |
| **Δ** | *capital delta* | "Change in" — e.g. `ΔPₜ` = price change at time t |

Read aloud: *"delta star equals gamma sigma squared times T minus t, plus two over gamma, log of one plus gamma over kappa."*

---

## The solution — three decisions, three formulas

Every market-making algorithm answers one of these:

| Decision | Mechanism |
|---|---|
| **How wide should my spread be?** | Optimal spread formula — wide enough to cover both risks, tight enough to fill |
| **Where do I center my spread?** | Reservation price — shifts off mid when I'm already holding inventory |
| **When do I step out of the market?** | Toxic flow detection — no formula; practical rules |

The next slides walk through each.

---

## Decision 1 — the spread (Avellaneda–Stoikov)

```
δ* = γσ²(T − t) + (2/γ) · ln(1 + γ/κ)
```

Two terms, two risks:

- **γσ²(T − t)** — compensates **inventory risk**. Wider when volatility is high, risk aversion is high, or time horizon is long.
- **(2/γ) · ln(1 + γ/κ)** — compensates **adverse selection**. Wider when fills are insensitive to your price (κ small) — meaning the flow is picking you off regardless of where you quote.

**Intuition:** spread = rent for warehousing risk + insurance premium against informed traders.

---

## Decision 2 — the center (reservation price)

```
r(s, q, t) = s − q · γ · σ² · (T − t)
```

- `q = 0` (flat): quote centred on mid `s`.
- `q > 0` (long): shade the whole spread **below** mid — you'd rather sell than buy more.
- `q < 0` (short): shade **above** — you'd rather buy than stay short.

Bid = `r − δ*/2`, Ask = `r + δ*/2`.

**Intuition:** when you're already holding something, every additional unit hurts you more (concave utility). Shift your quotes so the side that reduces inventory gets filled first.

---

## The foundation — why spreads exist (Roll model)

Before Avellaneda–Stoikov, Roll (1984) showed you can **infer** the spread from trade prices alone.

```
Cov(ΔPₜ, ΔPₜ₋₁) = −c²    where c = half-spread
```

Why negative? **Bid-ask bounce:** consecutive trades alternate between buyers (hitting the ask) and sellers (hitting the bid). Price ticks up, down, up, down around the true mid.

The spread itself decomposes into:
- Order-processing cost (fixed operational cost)
- Inventory cost (compensating risk #1)
- Adverse-selection cost (compensating risk #2)

**Takeaway:** every component of the spread has an economic reason. You can't quote tighter than your cost structure and survive.

---

## Decision 3 — when to step out (practice beats theory)

The model assumes continuous prices and stable order flow. Reality breaks these:

- **Discrete tick sizes** → you can't quote at `r ± δ*/2` exactly. Round and manage residuals.
- **Queue position** → being first at a price level is worth money (FIFO fills).
- **Make/take fees** → rebates flip the sign of marginal-trade P&L.
- **Toxic flow** → large aggressive prints, correlated-instrument moves, news events signal that your quote is about to be picked off.

**Rule of thumb:** widen on uncertainty, pull on conviction. A market maker who won't cancel won't survive.

Skewing in practice: long inventory → lower **both** bid and ask (not just reservation shift). Skew is nonlinear — small near zero, steep near position limits.

---

## When market making works — and doesn't

| Regime | Outcome | Why |
|---|---|---|
| Range-bound, high volume, tight spreads | **Works** | Spread capture dominates adverse selection |
| Trending markets | **Fails** | Inventory accumulates against the trend |
| News events | **Fails** | Adverse selection spikes faster than you can widen |
| Low liquidity, wide spreads | **Ambiguous** | Wider spread helps, but fills are sparse |

Market making is a **regime-dependent** strategy. The algos handle the first regime; discipline to step out handles the others.

---

## Validation — how do you know your MM is working?

You can't eyeball "am I making money" — the P&L is tiny per trade and swamped by inventory moves. Measure:

- **Spread capture** — average fill price vs mid at fill time. Should be roughly `δ*/2` per fill.
- **Inventory half-life** — how fast does `q` mean-revert to zero? Fast = healthy, slow = you're accumulating.
- **Fill asymmetry** — are one-sided fills (only ask hits, never bid) a warning sign of adverse selection or drift?
- **Adverse selection cost** — post-trade markout. For each fill, measure mid N seconds later. If you consistently bought before mid dropped / sold before it rose, you're being picked off.
- **Hit rate vs quote rate** — how often do your quotes fill at all? Too low means spread too wide; too high with losses means too tight.
- **Sharpe of the strategy, ex-inventory** — strip out directional inventory P&L to isolate the spread-capture skill.

If markout is negative and widening — widen spread or pull. If inventory half-life blows up — tighten skew.

---

## Phase 2 in one line

**Market making = rent out your balance sheet as a counterparty.** The spread is the rent; inventory risk and adverse selection are the costs that eat it; Avellaneda–Stoikov prices the rent correctly; practical rules tell you when to stop renting.

**Sessions ahead:**
- **S4** (done) — why the spread exists: Roll decomposition
- **S5** (next) — derive Avellaneda–Stoikov: reservation price + optimal spread
- **S6** — practical skewing, Guéant–Lehalle–Fernandez-Tapia, what textbooks miss
- **S7** — multi-level quoting, queue position, make/take, toxic flow. **Capstone:** comparison table across the three approaches.
