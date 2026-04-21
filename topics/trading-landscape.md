# Topic: Trading Landscape — Products, Roles, and Evaluation

## Why I Want to Learn This
I've been learning trading algorithms (`trading-algos` topic) but the math felt abstract without understanding what human traders actually do day-to-day. This course fills the operational gap: what each trader role does, what parameters they watch in production, and how the industry evaluates whether a trading decision was good or bad. Complements `trading-algos` (the math of strategies) with `trading-landscape` (the operational context that sits above it).

## Current Knowledge Level
Beginner on the operational/role side. Have infrastructure exposure (low-latency trading systems, feed handlers, order books) and intermediate exposure to execution and market-making math via the in-progress `trading-algos` topic.

## Goal
Be able to:
1. Describe what each major trader role (MM, speculator, execution desk, prop) does across equities, futures, options, FX, and rates.
2. Explain the key parameters traders act on in production — including the Greeks for options, with the naming-collision between Black-Scholes γ (measurement) and Avellaneda-Stoikov γ (preference) firmly internalised.
3. Evaluate whether a trading decision was good or bad using an ex-ante-vs-ex-post framework that separates skill from luck.

For each asset class: know the product mechanics, what the trader watches live, and how the role is evaluated.

## Capstone: what artefact proves mastery?
Whole-course capstone: `artefacts/trading-landscape/phase-7/trader-scorecard-template.md` — apply the ex-ante vs ex-post evaluation framework to one completed `trading-algos` session (e.g. the Session 1 VWAP execution algo), closing the loop between the two courses. One capstone per phase, listed in the plan's "Capstones by Phase" table.

## Resources
- Harris — "Trading and Exchanges: Market Microstructure for Practitioners" (breadth reference for Phases 1–2)
- Hull — "Options, Futures, and Other Derivatives" (Phase 3–4 reference; read selectively, not cover-to-cover)
- Lehalle & Laruelle — "Market Microstructure in Practice" (Phase 2, Phase 6)
- Taleb — "Dynamic Hedging" (Phase 4 options practice perspective)
- Bookstaber — "A Demon of Our Own Design" (operational risk context, Phase 7)
- Matt Levine — "Money Stuff" newsletter (ongoing industry colour)
- Sample blotter screenshots and trader UIs from public broker docs (IBKR, Bloomberg promotional material) for the "screen-of-the-day" opening ritual from Phase 2 onward

## Time Estimate
~23 sessions over ~8 weeks (3 sessions/week, ~1.5 hrs each)

## Priority
medium
