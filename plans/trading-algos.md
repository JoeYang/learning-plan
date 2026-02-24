# Learning Plan: Trading Algorithms & Strategies

**Start date:** 2026-02-09
**Target completion:** ~2026-03-22 (6 weeks)
**Schedule:** ~3 hours/week (3 sessions × ~1hr), flexible
**Status:** in-progress

---

## Phase 1: Execution Algorithms (Sessions 1-3)

### Session 1: TWAP & VWAP
**Objective:** Understand the two most fundamental execution algorithms — what they optimize and when to use each
- [x] TWAP: derived the formula (q_i = Q/T), timer-driven vs event-driven slicing
  - When to use: low urgency, no strong volume signal, thin markets
  - Implementation: Java multi-threaded with single-writer event loop pattern
- [x] VWAP: derived the formula (q_i = Q × V̂_i/V̂), optimal schedule from tracking error minimization
  - Volume profile: historical intraday U-shape, pre-computed cumulative fractions
  - Implementation: volume-driven pacemaker with price-sensitive execution (passive/aggressive logic)
  - Parent order limit price: hard ceiling that pauses the algo, with catch-up strategies
- [x] Pros/cons comparison: simplicity and transparency vs predictability to adversaries
- [x] Discussed TWAP/VWAP weakness in volatile markets → motivation for IS/Almgren-Chriss
- [x] Java implementation: single-threaded event loop, lock-free ring buffers, fixed-point prices, zero-allocation hot path
- [x] Data structures for time-based scheduling: sorted array (fixed schedules), min-heap (small timer count), timing wheel (many concurrent timers, O(1) insert/cancel)
**Notes:** VWAP dominates TWAP in liquid markets. Volume-driven approach 3 (opportunistic within windows) is production standard. Timer wheel is the go-to for managing many concurrent algo timers. Single-writer event-loop architecture avoids all locking.
**Key concepts:** TWAP formula, VWAP formula, volume profiles, market impact, benchmark tracking
**Resources:** Johnson "Algorithmic Trading and DMA" (execution algo chapters), QuantStart execution algo articles

### Session 2: Implementation Shortfall & Almgren-Chriss
**Objective:** Derive the Almgren-Chriss optimal execution model and understand the fundamental tradeoff
- [x] Implementation shortfall defined: slippage between decision price and execution price
- [x] Almgren-Chriss model — full derivation:
  - Setup: sell X shares over time T, arithmetic Brownian motion with impact
  - Temporary impact: η·v (spread/book depletion), Permanent impact: γ·v (information leakage)
  - Cost function: E[Cost] = ½γX² + η·Σ(n_k²/τ), Var[Cost] = σ²·Σ(τ·x_k²)
  - Euler-Lagrange → ODE: ẍ = κ²x where κ = √(λσ²/η)
  - Solution: x(t) = X·sinh(κ(T-t))/sinh(κT)
  - κ→0 recovers TWAP, κ→∞ is immediate execution
- [x] Efficient frontier: Pareto-optimal curve of E[cost] vs Var[cost], trader picks λ
- [x] Limit vs market IS orders: spread cost, fill certainty, adverse selection, timing risk tradeoffs
  - Market: guaranteed fill, pay spread, low timing risk — use when behind schedule, volatile, tight spread
  - Limit: earn spread, probabilistic fill, high adverse selection — use when ahead of schedule, calm, wide spread
  - Decision framework: schedule gap, volatility regime, spread width, momentum direction
- [x] Pros/cons: elegant closed-form but parameter estimation (η, γ) is garbage-in-garbage-out
**Notes:** κ is the urgency parameter — high vol means high κ means front-load execution. TWAP is Almgren-Chriss with λ=0. The limit/market decision within each slice is where real alpha lives in execution.
**Key concepts:** Implementation shortfall, temporary vs permanent impact, mean-variance optimization, execution frontier
**Resources:** Almgren & Chriss "Optimal Execution of Portfolio Transactions" (2000)

### Session 3: POV, Iceberg & Execution Algo Survey
**Objective:** Complete the execution algo toolkit and build a comparison framework
- [x] POV (Percentage of Volume): formula (trade at fixed % of observed volume)
  - Adaptive participation: adjust rate based on real-time volume
  - When to use: when you want to be a consistent fraction of the market
- [x] Iceberg/reserve orders: mechanics (show small size, reload from hidden reserve)
  - Detection by other participants: patterns that give icebergs away
- [x] Build comparison table of all execution algos:
  - Columns: algo, what it optimizes, inputs needed, market impact profile, predictability, complexity
  - Rows: TWAP, VWAP, IS/Almgren-Chriss, POV, Iceberg
- [x] Notes: the comparison table is the key deliverable — reference it when choosing algos later
**Key concepts:** POV formula, iceberg orders, execution algo selection, market impact profiles
**Resources:** Johnson "Algorithmic Trading and DMA", various execution algo survey papers

---

## Phase 2: Market Making (Sessions 4-7)

### Session 4: Market Making Fundamentals
**Objective:** Understand what a market maker does, how they profit, and what risks they face
- [x] What a market maker does: continuously quoting bid and ask, providing liquidity
- [x] Basic P&L model: spread capture minus adverse selection losses
  - Spread capture: earn (ask - bid)/2 on each round trip
  - Adverse selection: lose when informed traders trade against you
- [x] Inventory risk: why holding inventory is dangerous (directional exposure)
- [x] The bid-ask spread decomposition (Roll model):
  - Spread = f(order processing costs, inventory costs, adverse selection costs)
  - Derive the Roll model: Cov(ΔPt, ΔPt-1) = -c² where c = half-spread
- [x] Notes: sketch the market maker's P&L, annotate what kills profitability
**Key concepts:** Market making, spread capture, adverse selection, inventory risk, Roll model
**Resources:** Roll (1984) "A Simple Implicit Measure of the Effective Bid-Ask Spread", market microstructure lecture notes

### Session 5: Avellaneda-Stoikov Model — Derivation
**Objective:** Derive the foundational optimal market making model from first principles
- [ ] Setup: market maker quotes bid and ask around a mid-price following Brownian motion
  - Inventory q, risk aversion γ, volatility σ, time horizon T-t
  - Order arrivals follow Poisson process with intensity dependent on distance from mid
- [ ] Full derivation of reservation price:
  - r(s, q, t) = s - q·γ·σ²·(T-t)
  - Intuition: shade price away from mid in proportion to inventory and risk
- [ ] Full derivation of optimal spread:
  - δ* = γ·σ²·(T-t) + (2/γ)·ln(1 + γ/κ)
  - First term: compensation for inventory risk
  - Second term: compensation for adverse selection (κ = order arrival intensity parameter)
- [ ] Parameter estimation: how to estimate γ, σ, κ from data
- [ ] Notes: write out the complete derivation step by step, annotate each term's meaning
**Key concepts:** Reservation price, optimal spread, inventory adjustment, Poisson order arrivals, HJB equation
**Resources:** Avellaneda & Stoikov "High-frequency trading in a limit order book" (2008)

### Session 6: Inventory Management & Skewing
**Objective:** Bridge the gap between textbook models and practical market making
- [ ] Skewing quotes based on inventory (the practical version of Avellaneda-Stoikov):
  - When long: lower both bid and ask to encourage selling, discourage buying
  - When short: raise both bid and ask to encourage buying, discourage selling
- [ ] Guéant-Lehalle-Fernandez-Tapia extensions:
  - Closed-form solutions for optimal quotes with exponential utility
  - How they handle discrete tick sizes and finite inventory limits
- [ ] Practical considerations that break the textbook model:
  - Discrete tick sizes (can't quote at arbitrary prices)
  - Queue position value (being first at a price level matters)
  - Adverse selection signals (trade size, aggressor patterns, correlated instruments)
- [ ] Pros/cons: mathematical elegance of the models vs real-world messiness
- [ ] Notes: annotate where theory meets practice, what adjustments real market makers make
**Key concepts:** Quote skewing, inventory limits, tick size constraints, queue position, adverse selection signals
**Resources:** Guéant, Lehalle, Fernandez-Tapia "Dealing with the Inventory Risk" (2012)

### Session 7: Market Making in Practice
**Objective:** Understand how real market makers operate beyond the textbook models
- [ ] How real market makers differ from the Avellaneda-Stoikov model:
  - Multi-level quoting: posting at multiple price levels simultaneously
  - Queue position value: why being first in the queue at a price level has value
  - Make/take fee structures: maker rebates vs taker fees, and how they affect strategy
- [ ] Market making across correlated instruments:
  - Cross-instrument hedging (e.g., quote one instrument, hedge with another)
  - When correlation breaks: risk of basis blowup
- [ ] When market making works vs when it doesn't:
  - Works: range-bound markets, high volume, tight spreads, predictable flow
  - Fails: trending markets, news events, low liquidity, toxic flow
- [ ] Notes: list the practical considerations a real market making system must handle
**Key concepts:** Multi-level quoting, queue position, make/take fees, cross-instrument hedging, toxic flow
**Resources:** Market microstructure blog posts, Lehalle & Laruelle "Market Microstructure in Practice"

---

## Phase 3: Statistical Arbitrage (Sessions 8-11)

### Session 8: Pairs Trading & Cointegration
**Objective:** Understand cointegration and how to use it for pairs trading
- [ ] Cointegration vs correlation — why the distinction matters:
  - Correlated: prices move together (but can diverge permanently)
  - Cointegrated: spread between prices is mean-reverting (long-run equilibrium)
- [ ] Engle-Granger two-step test:
  - Step 1: regress Y on X, get residuals
  - Step 2: ADF test on residuals — if stationary, the pair is cointegrated
  - Derivation: why OLS residuals being stationary implies cointegration
- [ ] Johansen test for multiple cointegrated pairs:
  - When you have >2 assets, Johansen finds all cointegrating relationships
  - Eigenvalue-based approach (overview, not full derivation)
- [ ] Trading signals: z-score of the spread, entry at ±2σ, exit at 0
- [ ] Notes: work through a concrete example (two stocks), sketch the spread and signals
**Key concepts:** Cointegration, Engle-Granger test, ADF test, Johansen test, z-score signals
**Resources:** Engle & Granger (1987), Ernie Chan "Algorithmic Trading" (pairs trading chapter)

### Session 9: Mean Reversion — Ornstein-Uhlenbeck Process
**Objective:** Derive the OU process and use it to model mean-reverting spreads
- [ ] The Ornstein-Uhlenbeck process: dX = θ(μ - X)dt + σdW
  - θ = speed of mean reversion (higher = faster reversion)
  - μ = long-run mean
  - σ = volatility of the process
  - Full derivation from the SDE using the integrating factor method
- [ ] Parameter estimation from data:
  - Discrete-time AR(1) approximation: X(t+1) = a + b·X(t) + ε
  - θ = -ln(b)/Δt, μ = a/(1-b), σ from residual variance
  - Half-life of mean reversion: t½ = ln(2)/θ
- [ ] Optimal entry/exit thresholds:
  - Framework for choosing thresholds that maximize Sharpe ratio
  - Tradeoff: tighter thresholds = more trades but less profit per trade
- [ ] Pros/cons: elegant for stationary spreads, fails when regime changes or cointegration breaks
- [ ] Notes: derive the OU solution, estimate parameters on a sample spread, compute half-life
**Key concepts:** Ornstein-Uhlenbeck process, mean reversion speed, half-life, SDE solution, parameter estimation
**Resources:** Uhlenbeck & Ornstein (1930), Ernie Chan "Algorithmic Trading"

### Session 10: Kalman Filter for Dynamic Hedging
**Objective:** Apply the Kalman filter to dynamically estimate hedge ratios in pairs trading
- [ ] Kalman filter basics (state-space framework):
  - State equation: β(t) = β(t-1) + w(t) (hedge ratio evolves as random walk)
  - Observation equation: Y(t) = β(t)·X(t) + v(t)
  - The Kalman filter estimates β(t) optimally given noisy observations
- [ ] Derivation of the Kalman update equations in the pairs context:
  - Predict step: β̂(t|t-1) = β̂(t-1|t-1), P(t|t-1) = P(t-1|t-1) + Q
  - Update step: K(t) = P(t|t-1)·X(t) / (X(t)²·P(t|t-1) + R)
  - β̂(t|t) = β̂(t|t-1) + K(t)·(Y(t) - β̂(t|t-1)·X(t))
  - P(t|t) = (1 - K(t)·X(t))·P(t|t-1)
- [ ] Why Kalman beats static regression:
  - Adapts to changing relationships (non-stationary hedge ratios)
  - Provides confidence intervals on the hedge ratio estimate
- [ ] Practical tuning: choosing Q (process noise) and R (observation noise)
- [ ] Notes: implement the Kalman update equations on paper for a sample pairs trade
**Key concepts:** State-space model, Kalman gain, predict-update cycle, dynamic hedge ratio, process noise vs observation noise
**Resources:** Kalman (1960), Ernie Chan "Algorithmic Trading" (Kalman filter chapter)

### Session 11: Stat Arb Portfolio Construction
**Objective:** Scale from pairs to portfolios and understand the risks of statistical arbitrage
- [ ] From pairs to baskets: PCA-based stat arb:
  - Run PCA on a universe of returns
  - Eigenportfolios: portfolios defined by principal components
  - Trade mean-reverting combinations of eigenportfolios
- [ ] Eigenportfolios and mean-reverting principal components:
  - First few PCs capture market/sector factors (not mean-reverting)
  - Later PCs may capture mean-reverting stat arb opportunities
  - How to test which PCs are mean-reverting (OU parameter estimation)
- [ ] Risk management for stat arb:
  - Drawdown limits: when to stop trading a strategy
  - Correlation breakdown: what happens when all pairs diverge at once
  - Crowding risk: when too many funds trade the same pairs
- [ ] Case study: August 2007 quant crisis — what went wrong and lessons learned
- [ ] Notes: summarize the PCA approach, list the risk factors that kill stat arb
**Key concepts:** PCA, eigenportfolios, mean-reverting PCs, drawdown limits, crowding risk, 2007 quant crisis
**Resources:** Avellaneda & Lee "Statistical Arbitrage in the US Equities Market" (2010), Khandani & Lo (2007)

---

## Phase 4: Momentum & Trend Following (Sessions 12-14)

### Session 12: Moving Averages & Trend Detection
**Objective:** Derive the moving average formulas and understand their signal properties
- [ ] Simple Moving Average (SMA): formula, properties, lag = (N-1)/2 periods
- [ ] Exponential Moving Average (EMA): recursive formula EMA(t) = α·P(t) + (1-α)·EMA(t-1)
  - Derivation: show that EMA is an exponentially weighted sum of all past prices
  - Choosing α: relationship to span N via α = 2/(N+1)
  - EWMA variance estimator: σ²(t) = α·(r(t) - μ)² + (1-α)·σ²(t-1)
- [ ] Moving average crossover signals:
  - Golden cross (short MA crosses above long MA) = buy signal
  - Death cross (short MA crosses below long MA) = sell signal
  - Why this works: trend persistence, momentum
- [ ] Pros/cons: simple, robust, and well-understood vs lagging indicator, whipsaw in sideways markets
- [ ] Notes: derive EMA from the weighted sum, plot crossover signals on sample data
**Key concepts:** SMA, EMA, EWMA, crossover signals, lag, trend detection
**Resources:** Technical analysis foundations, Quantitative Trading blog posts

### Session 13: Breakout & Momentum Strategies
**Objective:** Understand momentum strategies and the evidence for why they work
- [ ] Donchian channel breakouts:
  - Entry: buy when price exceeds N-day high, sell when price breaks N-day low
  - The original trend-following system (Turtle Traders)
- [ ] Time-series momentum (Moskowitz, Ooi, Pedersen 2012):
  - Formula: signal = sign of past 12-month return, size by volatility target
  - Evidence: works across asset classes and time periods
  - Why it works: behavioral (underreaction, herding) and structural (hedging demand)
- [ ] Cross-sectional momentum:
  - Rank assets by past returns (e.g., 12-month minus most recent month)
  - Go long top decile, short bottom decile
  - Jegadeesh & Titman (1993): the foundational paper
- [ ] Momentum crashes and tail risk:
  - Momentum has negative skewness: occasional large drawdowns
  - Daniel & Moskowitz (2016): momentum crash dynamics
- [ ] Notes: compare time-series vs cross-sectional momentum, list tail risks
**Key concepts:** Donchian channels, time-series momentum, cross-sectional momentum, momentum crashes
**Resources:** Moskowitz, Ooi, Pedersen "Time Series Momentum" (2012), Jegadeesh & Titman (1993)

### Session 14: Trend Following in Practice
**Objective:** Understand how professional trend followers build and manage their systems
- [ ] CTA/managed futures style trend following:
  - Diversify across many markets (commodities, rates, FX, equities)
  - Use multiple timeframes (short, medium, long)
  - Combine signals: weighted average of trend signals across timeframes
- [ ] Position sizing for trend following:
  - Volatility targeting: size = (target vol × capital) / (instrument vol × point value)
  - Why volatility-adjusted sizing matters: equalizes risk across instruments
- [ ] Combining signals across timeframes and assets:
  - Signal aggregation: average trend signals across lookback periods
  - Portfolio-level vol targeting: scale entire portfolio to target volatility
- [ ] Pros/cons: "crisis alpha" (tends to profit in equity crashes) vs whipsaw losses in range-bound markets
- [ ] Notes: sketch a complete trend-following system from signal to position size
**Key concepts:** CTA strategies, multi-timeframe signals, volatility targeting, crisis alpha, whipsaw risk
**Resources:** AQR trend following research, Hurst, Ooi & Pedersen "A Century of Evidence on Trend-Following Investing" (2017)

---

## Phase 5: Signal Construction & Factor Models (Sessions 15-16)

### Session 15: Alpha Signals & Feature Engineering
**Objective:** Learn how to construct, evaluate, and combine trading signals
- [ ] What makes a good signal:
  - Predictive power (does it forecast returns?)
  - Decay rate (how quickly does the signal lose value?)
  - Capacity (how much capital can trade on it before it stops working?)
- [ ] Signal types:
  - Price-based: momentum, mean reversion, volatility
  - Volume-based: volume breakouts, VWAP deviation, order flow imbalance
  - Microstructure-based: bid-ask spread, book imbalance, trade arrival rate
  - Fundamental: earnings surprises, analyst revisions, macro data
- [ ] Information Coefficient (IC) and signal quality measurement:
  - IC = correlation between signal and forward returns
  - IC of 0.05 is already a strong signal in practice
  - IR (Information Ratio) = IC × √(breadth) — the fundamental law of active management
- [ ] Signal combination: linear weighting, z-score normalization, equal-weight vs optimized
- [ ] Notes: for each signal type, write one concrete example and how you'd measure its IC
**Key concepts:** Alpha signals, IC, IR, fundamental law of active management, signal decay, capacity
**Resources:** Grinold & Kahn "Active Portfolio Management", Kakushadze "101 Formulaic Alphas"

### Session 16: Factor Models
**Objective:** Understand factor models from CAPM to Fama-French and their practical use
- [ ] CAPM derivation and intuition:
  - E[Ri] = Rf + βi·(E[Rm] - Rf)
  - Beta = systematic risk, alpha = excess return above CAPM prediction
  - Limitations: single factor, assumes market efficiency
- [ ] Fama-French 3-factor model:
  - Add size (SMB = small minus big) and value (HML = high minus low book-to-market)
  - Derivation: sort stocks into portfolios by size and value, compute factor returns
- [ ] Fama-French 5-factor model:
  - Add profitability (RMW = robust minus weak) and investment (CMA = conservative minus aggressive)
  - What each factor captures and the economic intuition
- [ ] Practical use of factor models:
  - Alpha = return unexplained by known factors (the regression residual)
  - Risk decomposition: how much of portfolio risk comes from each factor
  - Performance attribution: was the return from alpha or factor exposure?
  - Hedging: neutralize unwanted factor exposures
- [ ] Notes: run a factor regression on paper, decompose a hypothetical portfolio's returns
**Key concepts:** CAPM, Fama-French factors, alpha, beta, risk decomposition, performance attribution
**Resources:** Fama & French (1993, 2015), Barra risk model documentation

---

## Phase 6: Risk & Position Sizing (Sessions 17-18)

### Session 17: Position Sizing & Kelly Criterion
**Objective:** Derive the Kelly criterion and compare practical position sizing approaches
- [ ] Kelly criterion derivation:
  - Setup: repeated bets with probability p of winning b, probability q=1-p of losing 1
  - Maximize E[log(wealth)] over many bets
  - Solution: f* = (bp - q) / b = p - q/b (fraction of capital to bet)
  - For continuous returns: f* = μ/σ² (bet proportional to Sharpe²)
- [ ] Fractional Kelly — why everyone uses half-Kelly or less:
  - Full Kelly is too aggressive (high variance, large drawdowns)
  - Half-Kelly: 75% of the growth rate with much lower variance
  - Parameter uncertainty: if you mis-estimate edge, full Kelly can be catastrophic
- [ ] Volatility targeting:
  - Position size = (target portfolio vol × capital) / (asset vol × notional per unit)
  - Why it's popular: simple, robust, doesn't require edge estimation
- [ ] Comparing approaches: Kelly vs equal-weight vs risk parity vs volatility targeting
  - Kelly: optimal if you know your edge exactly (you don't)
  - Equal-weight: simple, no estimation error, but ignores risk
  - Risk parity: equalize risk contribution from each position
  - Volatility targeting: practical middle ground
- [ ] Notes: derive Kelly, compute optimal fraction for a concrete example, compare to vol targeting
**Key concepts:** Kelly criterion, log-wealth maximization, fractional Kelly, volatility targeting, risk parity
**Resources:** Kelly (1956), Thorp "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market"

### Session 18: Portfolio Risk & Capstone
**Objective:** Tie everything together — portfolio optimization, risk metrics, and capstone comparison
- [ ] Mean-variance optimization (Markowitz):
  - Derivation of the efficient frontier: minimize σ²(w) subject to E[R(w)] = target
  - Lagrangian solution: w* = Σ⁻¹·μ / (1ᵀΣ⁻¹μ) (for max Sharpe)
  - Limitations: garbage-in-garbage-out (sensitive to estimated μ, Σ)
- [ ] Risk metrics — what each measures and when to use it:
  - Sharpe ratio: (return - Rf) / vol — reward per unit of total risk
  - Sortino ratio: (return - Rf) / downside vol — penalizes only downside
  - Max drawdown: largest peak-to-trough decline — measures tail risk
  - Calmar ratio: annualized return / max drawdown — return per unit of drawdown risk
- [ ] Risk budgeting across strategies:
  - Allocate risk budget (not capital) to each strategy
  - Correlation between strategies matters: diversification benefit
- [ ] Capstone exercise: pick 3 strategies from the course, write a 1-page comparison:
  - For each: the math (key formula), when to use it, implementation considerations, what could go wrong
  - How they complement each other in a portfolio
- [ ] Notes: the capstone comparison is the key deliverable of the entire course
**Key concepts:** Efficient frontier, Markowitz optimization, Sharpe/Sortino/Calmar ratios, max drawdown, risk budgeting
**Resources:** Markowitz "Portfolio Selection" (1952), Grinold & Kahn "Active Portfolio Management"
