# Quiz: Session 5 — Avellaneda-Stoikov Model

**Date:** 2026-04-21
**Score:** 8.5 / 10

**Instructions:** 7 multiple-choice + 3 short-answer. Answers at the bottom.

---

### Q1. What is the primary profit mechanism of a market maker?

A) Predicting short-term price direction and positioning ahead of the move
B) Earning the bid-ask spread when both sides of their quote fill against opposing flow
C) Buying assets below fair value and holding until mean reversion occurs
D) Arbitraging price differences between correlated instruments or venues

---

### Q2. An MM is long q = +50 shares. Mid-price is 100.00. With γ, σ², and T−t all positive, what does the Avellaneda-Stoikov reservation price tell them to do?

A) Center both quotes below mid, so the ask fills preferentially and reduces inventory
B) Raise both bid and ask above mid, charging a premium for carrying the long position
C) Keep the spread centered on mid but widen both sides to compensate for inventory
D) Cancel the bid entirely and quote ask-only until inventory returns to zero

---

### Q3. In the optimal spread δ* = γσ²(T−t) + (2/γ)·ln(1+γ/κ), what does the second term (2/γ)·ln(1+γ/κ) primarily compensate for?

A) Inventory risk — the danger that holding a position exposes you to price drift
B) Order-processing costs — exchange fees and infrastructure expenses per trade
C) Adverse selection — being picked off by informed traders with superior information
D) Queue position risk — the chance your order is not first in line at a price level

---

### Q4. You run an MM on an ETF. Realised volatility doubles after a macro announcement. Holding γ and κ fixed, what does Avellaneda-Stoikov tell you to do?

A) Widen the spread because σ² appears in the inventory-risk term γσ²(T−t), which makes inventory more dangerous
B) Tighten the spread because higher vol means more flow, and filling often reduces net inventory exposure
C) Keep spread unchanged because σ only enters the reservation price shift, not the spread width itself
D) Pull quotes entirely because the Brownian-motion assumption has been violated by a volatility jump

---

### Q5. Which statement about the reservation price r(s, q, t) = s − qγσ²(T−t) is INCORRECT?

A) When inventory q equals zero, the reservation price r reduces exactly to the current mid-price s
B) As trading time t approaches the horizon T, the inventory-shift magnitude shrinks toward zero
C) Higher risk aversion γ increases the magnitude of the reservation shift for any nonzero inventory
D) The reservation shift depends on |q| alone — whether q is positive or negative does not affect direction

---

### Q6. Your MM is being picked off — post-trade markouts are consistently negative within 3 seconds of fills. σ estimation tracks realised vol accurately. Inventory limits and risk tolerance unchanged. Most likely root cause?

A) γ is too low — you need to be more risk-averse, which would widen the quoted spread defensively
B) κ is over-estimated — your model assumes flow is more price-sensitive than it actually is
C) Parameter A is too high — you expect more baseline volume than the market is actually providing
D) The Brownian-motion assumption has broken and a jump-diffusion model would fit this regime better

---

### Q7. You're choosing γ for a new MM strategy. The hard constraint: 95th-percentile intraday drawdown must stay below 1.5% of capital. Which calibration approach fits best?

A) Kelly-style: γ* ≈ μ/σ² using backtested edge — maximises long-run growth rate
B) Sharpe-target: pick γ that maximises Sharpe in backtest — balances return vs total volatility
C) Inventory-limit: pick γ so spread-at-limit = 3× baseline — ties γ to business policy
D) Drawdown-constrained: pick γ so 95th-percentile simulated drawdown stays under the 1.5% target

---

### Q8. (Short answer) The volatility parameter σ (sigma) in Avellaneda-Stoikov describes what specific quantity? And which Greek symbol represents the steepness of order-arrival rate decay as quotes move further from mid?

**Rubric:**
- σ = volatility of the mid-price (stochastic / Brownian motion) — ½
- κ (kappa) = decay rate of arrival-rate function λ(δ) = A·exp(−κδ) — ½

---

### Q9. (Short answer) You suspect κ has shifted — flow has become less price-sensitive than your model assumes. Describe one specific diagnostic you would run on your historical quote-and-fill logs to confirm it.

**Rubric:**
- Full: bucket quotes by distance δ from mid, compute empirical arrival rate per bucket, regress ln(λ_emp) vs δ, compare slope to model κ
- Half: mention of arrival rate vs quote distance but without specifics
- Adjacent credit: markouts (consequence check, not direct κ fit) — half

---

### Q10. (Short answer) In one or two sentences, explain WHY the optimal spread formula has two separate terms instead of one, and what business-level meaning each carries.

**Rubric:**
- Full: names both inventory risk AND adverse selection; maps each term to the right risk
- Half: identifies one of the two correctly

---

## Answers

| Q | Answer | Joe's response | Credit |
|---|---|---|---|
| 1 | B | B | ✓ |
| 2 | A | A | ✓ |
| 3 | C | C | ✓ |
| 4 | A | A | ✓ |
| 5 | D | D | ✓ |
| 6 | B | B | ✓ |
| 7 | D | C (inventory-limit) | ✗ |
| 8 | σ = mid-price volatility; κ = arrival-rate decay | σ = vol of mid, κ = order arrival rate decay | ✓ full |
| 9 | Arrival-rate bucket regression of ln(λ) vs δ | Post-trade markouts | ½ (consequence, not direct fit) |
| 10 | Inventory risk + adverse selection = two business risks | "factor in inventory risk and risk adverse selection" | ✓ full |

**Final: 8.5 / 10**

### Weak areas to revisit

1. **γ-calibration method selection** — match the method to the operational constraint being enforced (drawdown → drawdown-fit, Sharpe target → Sharpe-fit, business policy → inventory-limit). Not one-size-fits-all.
2. **Direct κ diagnostic** — know the arrival-rate bucket regression, not just the markout consequence. Both belong in the MM diagnostics toolkit.
