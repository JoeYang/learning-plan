# Learning Plan: Trading Landscape — Products, Roles, and Evaluation

**Start date:** 2026-04-21
**Target completion:** ~2026-06-15 (~8 weeks)
**Schedule:** 3 sessions/week, ~1.5 hrs each
**Status:** in-progress

> Approach: breadth-first survey of the five asset classes (equities, futures, options, FX, rates) with a running "screen-of-the-day" opening ritual from Phase 2 onward to ground every session in what a trader actually stares at. Market making lives in its own late phase, operational-only — math lives in `trading-algos`.

---

## Capstones by Phase

A phase isn't closed until its capstone artefact exists under `artefacts/trading-landscape/phase-N/`.

| Phase | Capstone |
|---|---|
| Phase 1 (Ecosystem) | `artefacts/.../phase-1/ecosystem-map.md` — one-page diagram of players (PM, sell-side trader, MM, prop, HFT, venue, clearer) with arrows for order/risk/cash flow, annotated with where Joe's low-latency infra work fits. |
| Phase 2 (Equities) | `artefacts/.../phase-2/equity-trader-dashboard.md` — mock the blotter a cash equity trader watches (VWAP deviation, arrival slippage, markouts at 1s/10s/1m, queue depth), with written rationale for each field. |
| Phase 3 (Futures) | `artefacts/.../phase-3/basis-and-roll-memo.md` — 2-page memo walking through a concrete ES or CL roll. PnL decomposition into basis, carry, and roll cost, plus the trader's decision rule. |
| Phase 4 (Options) | `artefacts/.../phase-4/vol-surface-annotated.md` — annotated vol surface (skew/term-structure regimes) + a 5-day delta-hedging walk-through on a toy short-straddle book with PnL attribution to gamma/theta/vega. |
| Phase 5 (FX & Rates) | `artefacts/.../phase-5/carry-and-curve-trade.md` — one FX carry trade and one rates curve steepener, each with entry thesis, DV01/notional sizing, ex-ante risk, and kill criteria. |
| Phase 6 (MM across products) | `artefacts/.../phase-6/mm-comparison-matrix.md` — matrix with rows = products, columns = inventory horizon, hedge instrument, tick regime, toxic-flow signals, latency budget, fee structure. Filled with specifics, not generalities. |
| Phase 7 (Evaluation) | `artefacts/.../phase-7/trader-scorecard-template.md` + worked example — ex-ante decision-quality rubric vs ex-post P&L attribution applied to one completed `trading-algos` session. Closes the loop between the two courses. |

---

## Running thread: Screen-of-the-day

From Phase 2 onward, every Apply session opens with a **5-minute "screen-of-the-day"** — a mock or real screenshot of the exact blotter/screen a trader in that role stares at. The goal is to keep the sessions grounded in real workflow, not just concepts. Claude assembles the mock from public broker docs or public-domain examples; Joe reacts to what each field means and how a trader would read it at 9:31 a.m.

---

## Phase 1: The trading ecosystem (Sessions 1–3)

Survey all players, products, and the cross-cutting mechanics. No depth per product yet — that arrives in Phases 2–5.

**Phase 1 capstone:** `artefacts/trading-landscape/phase-1/ecosystem-map.md`

**Visual:** `docs/slides/trading-landscape/phase-1.md` — 5–10 slides on players, products, and mechanics. Rendered via `render-slides.py` for pre-read.

### Session 1: Players & the flow lifecycle
**Objective:** Build a mental model of who does what in trading, and what the end-to-end life of an order looks like.
- [ ] Sell-side vs buy-side — definitions, examples, revenue models
- [ ] Trader roles — market maker, speculator/prop, execution/agency, hedger/risk
- [ ] Flow lifecycle — PM → trader → algo → broker → venue → clearer → settlement
- [ ] Where infrastructure sits in the flow (where Joe's day-job work lives)
- [ ] Notes: sketch the flow diagram as Joe understands it before adding corrections
**Key concepts:** sell-side/buy-side, principal vs agency, prop vs client, flow lifecycle, clearing/settlement
**Resources:** Harris "Trading and Exchanges" Ch. 2–4, Matt Levine "Money Stuff" primer posts on market structure

### Session 2: Product survey across five asset classes
**Objective:** Know what trades, why, and how each asset class differs at a glance — the map before the terrain.
- [ ] Equities — what they are, why people trade them, primary vs secondary markets
- [ ] Futures — contract structure, margin, expiry, why they exist alongside spot
- [ ] Options — call/put basics, payoff shape, why use them (hedging, speculation, vol exposure)
- [ ] FX — the global spot/forward market, who the participants are
- [ ] Rates — Treasuries, swaps, the yield curve as a tradable object
- [ ] MM lens vignette — for each asset, one line on "how a market maker would quote this" (recurs in later phases)
- [ ] Notes: produce a one-row-per-asset comparison — typical participants, leverage, settlement, venue type
**Key concepts:** asset-class taxonomy, leverage, settlement, primary vs secondary, MM-lens framing
**Resources:** Hull "Options, Futures, and Other Derivatives" Ch. 1–2, Investopedia's asset-class primers for quick orientation

### Session 3: Cross-product mechanics
**Objective:** Internalise the mechanics that span every asset — the interface Joe's infra work actually sits on.
- [ ] Order types — IOC, FOK, post-only, hidden, iceberg, stop, stop-limit
- [ ] Venue mechanics — continuous matching, opening/closing auctions, dark pools, RFQ
- [ ] Clearing and settlement — CCPs, novation, T+1/T+2, margin vs variation
- [ ] Pre-trade risk — position limits, notional checks, fat-finger controls, kill switches
- [ ] P&L mechanics — mark-to-market vs realized, funding costs (repo, stock-loan), fees & rebates
- [ ] Rules of the game — best-ex obligations (Reg NMS, MiFID II best-ex), at a high level
- [ ] Notes: this session's value is as a reference map; revisit these concepts per-product later
**Key concepts:** order types, auction mechanics, CCP/clearing, pre-trade risk, MtM vs realized P&L, funding, rebates
**Resources:** Harris "Trading and Exchanges" Ch. 5–7, exchange rulebook excerpts (NYSE, CME, Eurex) — read one rulebook opening-auction section

---

## Phase 2: Equities (Sessions 4–6)

Deliberately does NOT re-derive IS/VWAP (covered in `trading-algos` Sessions 1–3). This phase is the **consumer/audit side**: how a human trader reads what those algos produce.

**Phase 2 capstone:** `artefacts/trading-landscape/phase-2/equity-trader-dashboard.md`

**Visual:** `docs/slides/trading-landscape/phase-2.md` — 5–10 slides on equity microstructure and trader workflow.

### Session 4: Cash equity microstructure
**Objective:** Understand the fragmented venue landscape equity traders navigate and the rules that govern it.
- [ ] Screen-of-the-day — a fragmented consolidated tape for a US large-cap
- [ ] Lit venues (NYSE, Nasdaq, IEX), dark pools, ATSs — what distinguishes each
- [ ] Fragmentation — SIP vs direct feeds, latency arbitrage, SOR (smart order routers)
- [ ] Block trading and RFQ for size — when the lit book isn't the right venue
- [ ] Reg NMS (US) and MiFID II best-ex (EU) — how they shape routing decisions
- [ ] LULD (limit up / limit down) and halts — what breaks the market and how traders react
- [ ] Notes: list the venues an equity trader might route to and why they'd pick each
**Key concepts:** venue fragmentation, SOR, dark pools, best-ex, LULD, SIP vs direct feeds
**Resources:** Harris "Trading and Exchanges" Ch. 8–10, SEC Reg NMS Rule 611 (skim), ESMA MiFID II overview

### Session 5: Live equity trader workflow
**Objective:** Know what an equity trader stares at from 9:30 to 4:00 and why.
- [ ] Screen-of-the-day — a mock of a live equity blotter (positions, P&L, orders, market data)
- [ ] The blotter — what each column means and what triggers a trader action
- [ ] Live markouts at 1s / 10s / 1m — reading toxicity in real time
- [ ] Reversion vs continuation — how a trader distinguishes mean-reverting from trending flow
- [ ] Event handling — news triage, corporate actions, macro data releases
- [ ] Notes: for each field on the blotter, write one sentence on what the trader does if it changes
**Key concepts:** blotter, markouts, reversion, event-driven trading, news triage
**Resources:** Lehalle & Laruelle "Market Microstructure in Practice" Ch. 4, IBKR/Bloomberg product docs for blotter UI references

### Session 6: Post-trade audit — reading the reports
**Objective:** Be able to pick up a post-trade report and extract the story — what the algo did and whether it did it well.
- [ ] Screen-of-the-day — a TCA (transaction cost analysis) report
- [ ] Implementation shortfall report — fields, sign conventions, common decompositions
- [ ] VWAP capture report — tracking error, where the algo deviated from benchmark
- [ ] Markout reports — ex-post signals of adverse selection
- [ ] Spotting attribution tells — volume surge, adverse event, latency outlier, wrong benchmark choice
- [ ] Notes: draft a short "reading this report" checklist
**Key concepts:** TCA, IS report, VWAP capture, markout tables, attribution
**Resources:** BMO/Virtu TCA product docs (public material), Perold "The Implementation Shortfall" (1988) for context — but read as consumer not author

---

## Phase 3: Futures (Sessions 7–10)

Expanded from 3 to 4 sessions (per Plan-agent review) — basis, roll, and calendar spreads each need room.

**Phase 3 capstone:** `artefacts/trading-landscape/phase-3/basis-and-roll-memo.md`

**Visual:** `docs/slides/trading-landscape/phase-3.md` — 5–10 slides covering contracts, basis, term structure, and trader workflow.

### Session 7: Contracts & mechanics
**Objective:** Understand the product — what a futures contract actually is and how margin works.
- [ ] Screen-of-the-day — a CME futures contract spec page
- [ ] Contract specs — tick size, multiplier, expiry, delivery (physical vs cash), CTD (cheapest-to-deliver)
- [ ] Initial margin vs variation margin — how daily mark-to-market works
- [ ] Expiry mechanics — last trading day, final settlement, physical delivery vs cash
- [ ] Notes: walk through a single contract (e.g. ES or CL) end-to-end from open trade to settlement
**Key concepts:** contract spec, margin, variation, CTD, expiry, settlement
**Resources:** CME product specs pages, Hull Ch. 2–3

### Session 8: Basis & calendar spreads
**Objective:** Understand the relationship between futures and spot, and the trades that exploit it.
- [ ] Screen-of-the-day — a basis quote screen (cash-futures basis for a Treasury or commodity)
- [ ] Basis definition — spot vs futures, drivers (carry, convenience yield, storage)
- [ ] Basis decomposition — what moves the basis day-to-day
- [ ] Calendar spreads — trading front-month vs back-month, why they exist, who trades them
- [ ] Notes: walk through a concrete basis example for one commodity and one financial future
**Key concepts:** basis, carry, convenience yield, calendar spread, curve shape
**Resources:** Hull Ch. 5, CME educational whitepapers on basis

### Session 9: Term structure & roll
**Objective:** Read a futures curve and understand what a roll actually costs.
- [ ] Screen-of-the-day — a full futures term-structure curve (WTI or corn)
- [ ] Contango vs backwardation — what each signals, historical examples
- [ ] Carry and roll yield — the mechanics of rolling a long-held futures position
- [ ] Roll window dynamics — volume migration from front to back month, how traders navigate it
- [ ] Roll P&L decomposition — carry, basis move, roll cost
- [ ] Notes: compute the carry on a hypothetical ES or CL position rolling from front to back
**Key concepts:** contango, backwardation, carry, roll yield, roll window, term structure
**Resources:** Hull Ch. 5, Moskowitz/Ooi/Pedersen on carry as a factor, CME roll-timing whitepapers

### Session 10: Futures trader workflow & evaluation
**Objective:** Know what a futures trader does during the roll window and how performance is judged.
- [ ] Screen-of-the-day — a roll-execution blotter around a contract expiry
- [ ] Roll-window trading — how execution desks handle the migration, timing tradeoffs
- [ ] Basis risk — when the hedge doesn't match the underlying exposure
- [ ] Evaluation — carry as P&L source, roll cost as drag, basis risk as tail
- [ ] Notes: sketch the futures trader's day from pre-open through roll-heavy weeks
**Key concepts:** roll-window trading, basis risk, carry P&L, evaluation metrics for futures desks
**Resources:** Lehalle & Laruelle Ch. 5 (futures-specific practice), public broker commentary on roll windows

---

## Phase 4: Options (Sessions 11–14)

The Greek-letter naming collision with `trading-algos` Avellaneda-Stoikov is called out explicitly in Session 12 — this is the pedagogical payoff for the whole course structure.

**Phase 4 capstone:** `artefacts/trading-landscape/phase-4/vol-surface-annotated.md` + 5-day delta-hedging walk-through.

**Visual:** `docs/slides/trading-landscape/phase-4.md` — 5–10 slides on payoffs, Greeks, vol surface, and options MM.

### Session 11: Payoffs & put-call parity
**Objective:** Internalise option payoffs and the algebraic relationships between calls, puts, and the underlying.
- [ ] Screen-of-the-day — an option chain for a liquid equity
- [ ] Call and put payoffs — diagrams at expiry, long vs short positions
- [ ] Put-call parity — derivation and intuition: `C − P = S − K·e^(−rT)`
- [ ] Synthetic positions — building a synthetic long, synthetic short, synthetic stock
- [ ] American vs European options — early-exercise considerations
- [ ] Dividends and borrow — how they shift parity and pricing
- [ ] Notes: draw each payoff diagram; verify put-call parity on a sample chain
**Key concepts:** payoff diagrams, put-call parity, synthetics, early exercise, dividends, borrow cost
**Resources:** Hull Ch. 10–11, Natenberg "Option Volatility & Pricing" Ch. 1–3

### Session 12: Greeks-as-trader-uses-them — and the naming-collision debrief
**Objective:** Know what each Greek measures on a real option book, and resolve the γ naming collision with `trading-algos`.
- [ ] Screen-of-the-day — a Greeks-view on an options blotter (aggregated δ, γ, θ, vega)
- [ ] Delta (δ) — directional exposure, hedge ratio, how a trader thinks about "delta-neutral"
- [ ] Gamma (γ) — convexity, the rate of change of delta, why gamma traders exist
- [ ] Theta (θ) — time decay, the rent you pay to hold long options
- [ ] Vega — sensitivity to implied vol, the core of a vol book
- [ ] Rho (ρ) — interest-rate sensitivity, usually small but matters for long-dated
- [ ] **Naming-collision debrief** — contrast Black-Scholes γ (a measured convexity quantity) with Avellaneda-Stoikov γ (a chosen risk-aversion preference). Same letter, opposite epistemology.
- [ ] Notes: for each Greek, one scenario where a trader acts specifically on that Greek
**Key concepts:** δ γ θ vega ρ, delta-neutral, gamma trading, vega book, Greek-letter naming collision
**Resources:** Hull Ch. 19, Natenberg Ch. 7–9, Taleb "Dynamic Hedging" (Greeks chapters)

### Session 13: Implied vol & the vol surface
**Objective:** Read an implied-vol surface and know what skew, smile, and term structure tell a trader.
- [ ] Screen-of-the-day — a 3D or heat-map vol surface for a liquid underlying
- [ ] Implied vol mechanics — invert Black-Scholes for σ given market option prices
- [ ] Skew — why OTM puts are often richer than OTM calls (crash risk premium)
- [ ] Smile — the U-shape around ATM, what it says about fat tails
- [ ] Term structure — near-term vs far-term, event pricing (earnings, macro)
- [ ] Vol cones — implied vs realised vol over different horizons
- [ ] Notes: annotate a sample vol surface with the current regime story (risk-on, risk-off, event-driven)
**Key concepts:** implied vol, skew, smile, term structure, vol cones, event-implied vs background vol
**Resources:** Natenberg Ch. 13–14, Derman "Volatility Smile" papers, public vol-surface tools (SpotGamma, OptionMetrics docs)

### Session 14: Options market making & delta-hedging
**Objective:** Understand how an options MM operates day-to-day, and walk through delta-hedging mechanics.
- [ ] Screen-of-the-day — an options MM's book view (Greeks aggregated, hedge P&L, residual risk)
- [ ] Options MM mindset — quote around implied vol, not price. Manage vega and gamma books separately.
- [ ] Delta-hedging — the pipeline from option fill to underlying hedge, latency tradeoffs
- [ ] Gamma-theta tradeoff — long gamma pays theta rent, short gamma earns theta
- [ ] Event risk — earnings, rate decisions, how MMs widen and hedge preemptively
- [ ] Notes: walk through a 5-day delta-hedging simulation on a toy short-straddle book → attribute P&L to γ, θ, vega (this feeds the capstone)
**Key concepts:** options MM, delta-hedging pipeline, gamma-theta tradeoff, vega book, event hedging
**Resources:** Taleb "Dynamic Hedging" Ch. 2–4, Lehalle & Laruelle Ch. 6

---

## Phase 5: FX & Rates (Sessions 15–18)

Expanded from 3 to 4 sessions — FX and rates each deserve dedicated workflow sessions.

**Phase 5 capstone:** `artefacts/trading-landscape/phase-5/carry-and-curve-trade.md`

**Visual:** `docs/slides/trading-landscape/phase-5.md` — 5–10 slides on FX mechanics, rates curves, and workflows.

### Session 15: FX mechanics
**Objective:** Understand the global FX market structure and the core product set.
- [ ] Screen-of-the-day — an FX trader's crosses and fixings screen
- [ ] Spot, forward, swap, NDF — what each product is and when it's used
- [ ] Major crosses vs crosses vs exotics — liquidity tiers
- [ ] Carry trade — mechanics, historical performance, crash risk
- [ ] Central-bank influence — how rate differentials and policy drive FX
- [ ] Notes: walk through a concrete forward quote and decompose the carry
**Key concepts:** spot/forward/swap/NDF, crosses, carry trade, interest-rate parity
**Resources:** Hull Ch. 5 (forwards) + Ch. 34 (FX-specific), BIS triennial FX survey

### Session 16: FX trader workflow & evaluation
**Objective:** Know what an FX trader watches intraday and how the desk is judged.
- [ ] Screen-of-the-day — an FX voice-broker or e-trading blotter
- [ ] Intraday regime — Tokyo/London/NY open/close dynamics, liquidity by session
- [ ] Fixings — the London 4pm fix, WMR methodology, why fixings matter for P&L
- [ ] Macro events — central-bank meetings, NFP, CPI — how FX desks pre-position
- [ ] Evaluation — carry P&L, realised-vol capture, hit rate, fixing slippage
- [ ] Notes: sketch the FX trader's 24-hour clock and note where liquidity lives
**Key concepts:** FX session dynamics, fixings, macro-event positioning, FX P&L attribution
**Resources:** Lyons "The Microstructure Approach to Exchange Rates" (selected chapters), BIS FX market commentaries

### Session 17: Rates mechanics
**Objective:** Understand the rates product set and the curve as a tradable object.
- [ ] Screen-of-the-day — a rates curve (Treasuries + OIS + swaps)
- [ ] The yield curve — Treasuries, OIS, swap curve, how they relate
- [ ] DV01 — dollar value of a basis point, sizing a rates trade
- [ ] Treasury mechanics — auctions, on-the-run vs off-the-run, repo financing
- [ ] Swaps — fixed-for-floating, par swap rate, swap curve construction
- [ ] OIS/SOFR transition — post-LIBOR reality, why it matters
- [ ] Notes: compute DV01 for a hypothetical 10yr position and a 2s10s steepener
**Key concepts:** yield curve, DV01, Treasuries, swaps, OIS, SOFR, repo
**Resources:** Hull Ch. 4 + Ch. 7, Fabozzi "Bond Markets, Analysis, and Strategies" (selected chapters), ISDA SOFR transition materials

### Session 18: Rates trader workflow & evaluation
**Objective:** Know what rates traders do (curve trades, RV, duration management) and how they're judged.
- [ ] Screen-of-the-day — a curve/RV (relative value) monitor
- [ ] Curve trades — steepeners, flatteners, butterflies. Sizing by DV01.
- [ ] Relative value — cash vs swap, on-the-run vs off-the-run basis
- [ ] ALM (asset-liability management) context — why rates matter outside prop
- [ ] Evaluation — DV01-neutral P&L attribution, convexity contribution, roll-down
- [ ] Notes: design a steepener trade and sketch its P&L under +25bp, 0bp, −25bp scenarios
**Key concepts:** curve trades, RV, ALM, DV01-neutral sizing, roll-down, convexity
**Resources:** Fabozzi, Tuckman "Fixed Income Securities" Ch. 5–8

---

## Phase 6: Market making across products (Sessions 19–21)

Expanded from 2 to 3 sessions — this is Joe's day-job-relevant phase. Strictly operational — no re-derivation of Avellaneda-Stoikov (covered in `trading-algos` Phase 2).

**Phase 6 capstone:** `artefacts/trading-landscape/phase-6/mm-comparison-matrix.md`

**Visual:** `docs/slides/trading-landscape/phase-6.md` — 5–10 slides on MM mindset, per-product differences, and infrastructure.

### Session 19: MM mindset across products
**Objective:** Consolidate the MM mental model from `trading-algos` into an operational framing across asset classes.
- [ ] Screen-of-the-day — an MM's inventory heatmap across multiple symbols
- [ ] The MM mindset recap — stateless, two-sided, inventory-aware. No directional view.
- [ ] What MMs stare at — inventory, queue position, toxic-flow signals, event calendar
- [ ] Hedging vs warehousing — when to offset, when to hold
- [ ] Notes: re-state the Phase 2 trading-algos concepts in operational language (no formulas)
**Key concepts:** MM mindset recap, inventory heatmap, queue, toxic flow, hedge-vs-warehouse decisions
**Resources:** Lehalle & Laruelle Ch. 7, public MM firm blogs (Jump, Optiver, IMC) when available

### Session 20: Per-product MM differences
**Objective:** Know how MM operationally differs across equities, futures, options, and FX.
- [ ] Screen-of-the-day — an MM's multi-product dashboard
- [ ] Equity MM — tick size regime, queue position value, maker rebates
- [ ] Futures MM — roll-period gyrations, tighter spreads near expiry, cross-contract hedges
- [ ] Options MM — vol quoting (not price quoting), vega book, delta hedging as a pipeline
- [ ] FX MM — 24h market, fixings, liquidity aggregation from multiple ECNs
- [ ] Notes: fill in the first draft of the MM-comparison-matrix capstone here
**Key concepts:** per-product MM differences, inventory horizon, hedge instrument, tick regime, toxic-flow signals
**Resources:** Lehalle & Laruelle Ch. 7, Taleb "Dynamic Hedging" (options MM perspective)

### Session 21: MM infrastructure
**Objective:** Tie MM operations to the infrastructure layer Joe works on.
- [ ] Screen-of-the-day — a latency monitor and quote-engine dashboard
- [ ] Queue dynamics — FIFO matching, where queue position matters most
- [ ] Latency budgets — market data → quote decision → order out; where nanoseconds live
- [ ] Hedging pipelines — the handoff from options fill to delta-hedge, batching tradeoffs
- [ ] Kill switches and safety — pre-trade risk, automatic quote pulls, manual overrides
- [ ] Notes: annotate a generic MM architecture diagram with where Joe's work lives
**Key concepts:** queue dynamics, latency budget, hedging pipeline, kill switch, pre-trade risk
**Resources:** FIX protocol docs (for order-entry mechanics), public conference talks on HFT infra (STAC, High Performance Computing Conference proceedings)

---

## Phase 7: Evaluation framework (Sessions 22–23)

Repurposed away from Sharpe/Sortino/Calmar definitions (those live in `trading-algos` Session 18). Focus is on **process vs outcome** and **skill vs luck** — the frameworks that prevent result-oriented thinking.

**Phase 7 capstone (also whole-course capstone):** `artefacts/trading-landscape/phase-7/trader-scorecard-template.md` applied to one completed `trading-algos` session.

**Visual:** `docs/slides/trading-landscape/phase-7.md` — 5–10 slides on ex-ante vs ex-post and skill-vs-luck frameworks.

### Session 22: Ex ante vs ex post
**Objective:** Learn to separate decision quality from outcome quality — the core of trader evaluation.
- [ ] Screen-of-the-day — a post-trade review meeting agenda
- [ ] The 2x2 — good decision / bad decision × good outcome / bad outcome. Four quadrants, four lessons.
- [ ] Process rubric — was the information available, was the thesis sound, was sizing correct, was the kill criterion clear
- [ ] P&L attribution — was the return from edge or from luck (market drift, beta, a lucky fill)
- [ ] When a bad outcome was a good decision — and vice versa
- [ ] Notes: apply the 2x2 to a recent trading decision (yours or a documented one)
**Key concepts:** decision-quality 2x2, process rubric, attribution, result-oriented thinking
**Resources:** Duke "Thinking in Bets" Ch. 1–3, Bookstaber "A Demon of Our Own Design" (operational risk context)

### Session 23: Skill vs luck
**Objective:** Apply statistical lenses that separate skill from luck — the discipline that kills false-positive strategies.
- [ ] Screen-of-the-day — a Sharpe distribution from bootstrap resampling
- [ ] Sample-size traps — how many trades to trust a Sharpe estimate
- [ ] Bootstrap resampling — constructing a null distribution for a strategy's returns
- [ ] Deflated Sharpe Ratio (Bailey & López de Prado) — adjusting for multiple-testing bias
- [ ] Why most backtested alpha doesn't survive — the survivorship and look-ahead pitfalls
- [ ] Notes: apply one of these tests to a simulated strategy result; see how the "significance" changes
**Key concepts:** sample-size, bootstrap, deflated Sharpe, survivorship bias, look-ahead bias
**Resources:** Bailey & López de Prado "The Deflated Sharpe Ratio" (2014), López de Prado "Advances in Financial Machine Learning" Ch. 8

---

## Closing the loop

The whole-course capstone applies Phase 7's framework to one completed `trading-algos` session. Example: take the Session 1 VWAP execution notes, score the decision quality ex ante (was benchmark choice sound? was urgency right?), score the outcome ex post (did realised VWAP capture match expectation?), and classify the session into one of the 2x2 quadrants. That artefact is the final proof of mastery — and the bridge between the two courses.
