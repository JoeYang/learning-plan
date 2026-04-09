# Day 13 (Tue Apr 21) -- Observability, Incident Response & Production Practices

## Overview (5 min)

Production excellence is not optional at a trading firm -- it is the difference between making money and losing money. A trading system that is down for 5 minutes during a volatile market event can cost millions. Jump Trading's Futures Execution Services team does not just build systems; they operate them in one of the most demanding production environments in software engineering. This day covers how to monitor, alert on, respond to, and prevent production issues in trading systems. Your Goldman Sachs experience with incident triage and production operations is directly relevant here.

---

## Reading Materials (60-90 min)

### 1. Monitoring Philosophy

Monitoring is not about dashboards -- it is about answering questions. The two dominant frameworks for thinking about what to monitor are USE and RED.

**USE Method (for infrastructure/resources)**

Created by Brendan Gregg, USE stands for:
- **Utilization**: How busy is the resource? (CPU at 80%, disk at 90%)
- **Saturation**: How much work is queued? (run queue length, swap usage)
- **Errors**: How many errors? (network CRC errors, disk I/O errors)

Apply USE to every resource in your system:

```
Resource          Utilization           Saturation              Errors
──────────────────────────────────────────────────────────────────────────
CPU               % time busy           Run queue length        Machine checks
Memory            % used                Swap usage              OOM kills
Network (NIC)     Bandwidth %           Ring buffer drops       CRC errors
Disk              % I/O time            Wait queue length       Read/write errors
Kernel buffers    Socket buffer usage   Buffer overflow count   Drop count
```

**In a trading context**, USE is particularly important for:
- NIC ring buffer saturation: If the NIC buffer overflows, you DROP market data packets. This is silent data loss.
- CPU saturation on the hot-path core: If the strategy thread cannot keep up with market data, it falls behind and trades on stale data.
- Memory utilization: Approaching memory limits risks OOM kills, which terminate your trading process instantly.

**RED Method (for services/requests)**

Created by Tom Wilkie, RED stands for:
- **Rate**: Requests per second (or messages per second in trading)
- **Errors**: Failed requests per second
- **Duration**: Latency distribution (p50, p99, p999)

Apply RED to every service boundary:

```
Service Boundary         Rate                  Errors              Duration
──────────────────────────────────────────────────────────────────────────────
Feed handler             Messages/sec per feed  Decode errors       Decode latency
Book builder             Updates/sec per book   Invalid updates     Book update latency
Strategy engine          Signals/sec            Risk rejections     Signal-to-order latency
Order gateway            Orders/sec             Rejects/timeouts    Order-to-ack latency
Exchange connection      Msgs/sec both dirs     Session errors      Round-trip latency
```

**Combining USE and RED**

USE tells you WHY something is slow (resource constraint). RED tells you THAT something is slow (service behavior). Use RED to detect problems, then USE to diagnose root causes.

```
Alert: Order gateway p99 latency exceeded 500us
  |
  +--> Check RED: Latency spike started at 10:15 AM
  |
  +--> Check USE: CPU utilization on gateway host jumped to 95%
  |
  +--> Root cause: A new risk check was added that performs
       an expensive computation on every order
```

### 2. SLI/SLO Design for Trading Systems

**SLI (Service Level Indicator)**: A quantitative measure of a service's behavior.
**SLO (Service Level Objective)**: A target value for an SLI.

Standard SLOs (availability: 99.99%) do not capture what matters in trading. You need trading-specific SLOs.

**Trading-Specific SLIs and SLOs**

```
SLI                              Measurement                    SLO
──────────────────────────────────────────────────────────────────────────
Order latency (p50)              Time from signal to order      < 5 us
Order latency (p99)              on wire                        < 20 us
Order latency (p999)                                            < 100 us

Fill rate                        Fills received / orders sent   > 98%

Market data freshness            Age of latest book update      < 100 us

Uptime during market hours       % of trading minutes with      99.99%
                                 all systems operational         (< 3 min/month)

Gap recovery time                Time to recover from           < 500 ms
                                 market data gap

Order reconciliation             Orders matching between        100%
                                 OMS and exchange records
```

**Why "Four Nines" During Market Hours**

Trading systems only need to be operational during market hours (typically 6.5 hours for US equities, but futures trade nearly 23 hours/day). Four nines (99.99%) during trading hours means less than 8 seconds of downtime per day. This is the realistic target -- any more downtime directly translates to lost trading opportunity.

**Error Budget**

The error budget is the inverse of the SLO: if your SLO is 99.99% uptime, your error budget is 0.01% (~50 seconds per month). When you have consumed your error budget:
- Freeze non-critical deployments
- Focus engineering effort on reliability
- Escalate to leadership

This creates a data-driven conversation about the trade-off between feature velocity and reliability.

### 3. Alerting

**Signal vs Noise**

The goal of alerting is to notify humans only when they need to act. Bad alerting (too many false positives) leads to alert fatigue, where operators ignore alerts -- including real ones.

**Alerting Principles**

1. **Alert on symptoms, not causes**. Alert when order latency exceeds the SLO, not when CPU is at 80%. High CPU might be fine if latency is fine.

2. **Every alert must have a runbook**. If you cannot write a runbook for an alert, the alert should not page a human. It should be a dashboard metric instead.

3. **Alerts should be actionable**. The person who receives the alert should be able to DO something about it. "Market data feed latency > 100us" is actionable. "Disk space > 70%" is not urgent and should not page.

4. **Use severity levels that map to response times**:

```
Severity   Response Time   Example
─────────────────────────────────────────────────────────────
P1 / SEV1  Immediate       Trading system down during market hours
           (< 5 min)       All orders failing
                           Market data feed completely lost

P2 / SEV2  Within 15 min   Degraded performance (latency 2x normal)
                           Single feed handler failover
                           Risk system stale

P3 / SEV3  Within 1 hour   Non-critical component degraded
                           Monitoring system partial failure
                           Elevated error rate on cold path

P4 / SEV4  Next business   Disk space warning
           day             Log ingestion lag
                           Non-market-hours system issue
```

**Alert Fatigue Mitigation**

- Group related alerts (suppress downstream alerts when an upstream failure is detected)
- Auto-resolve alerts that recover (do not leave stale alerts open)
- Review alert frequency monthly: if an alert fires > 5 times without requiring action, tune or remove it
- Separate "informational" alerts (dashboard/Slack) from "actionable" alerts (pager)

### 4. Incident Management

**Incident Lifecycle**

```
Detection ──> Triage ──> Mitigation ──> Resolution ──> Postmortem
  (alert)    (assess)   (stop the      (fix root     (learn and
              severity)  bleeding)       cause)         prevent)
```

**Detection**: Automated alerts or human observation. In trading, time-to-detection must be seconds, not minutes. Latency monitoring and order rejection rate monitoring are the primary detection signals.

**Triage**: Quickly assess severity and blast radius.
- Is it affecting trading? (P1 if yes)
- How many instruments/strategies are impacted?
- Is it getting worse or stable?

**Mitigation**: Stop the bleeding before diagnosing the root cause.
- Kill switch: disable all order submission if the system is sending bad orders
- Failover: switch to backup feed handler, backup gateway
- Rollback: revert the last config/code change if it correlates with the incident
- Manual override: disable the affected strategy while keeping others running

**Resolution**: Fix the root cause after the immediate impact is mitigated.

**Postmortem**: Learn from the incident. This is where organizational reliability improves.

**Blameless Postmortems**

Trading firms have high stakes, which creates pressure to blame individuals. Blameless postmortems resist this:

```
Postmortem Template:
─────────────────────────────────────────────────
1. Incident Summary
   - What happened? (1-2 sentences)
   - Duration and impact (quantified)
   
2. Timeline
   - Minute-by-minute from detection to resolution
   - Include what was tried and what worked/failed

3. Root Cause Analysis
   - Use "5 Whys" to dig past symptoms
   - Why did the system fail? (proximate cause)
   - Why wasn't it caught earlier? (detection gap)
   - Why was the system vulnerable? (systemic cause)

4. Contributing Factors
   - What made the incident worse or harder to resolve?
   - (e.g., missing monitoring, unclear runbook, etc.)

5. Action Items
   - Each item: owner, deadline, priority
   - Categorize: prevent recurrence, improve detection,
     improve mitigation, improve communication

6. Lessons Learned
   - What went well? (celebrate good incident response)
   - What should change?
─────────────────────────────────────────────────
```

**"5 Whys" Example**:
```
Symptom: Order gateway sent orders with stale prices for 30 seconds.

Why? The feed handler stopped publishing updates.
Why? The feed handler process crashed due to OOM.
Why? A memory leak in the SBE decoder accumulated over 3 days.
Why? The leak was not caught by testing because tests run for seconds, not days.
Why? There is no long-running soak test for the feed handler.

Action: Add a 24-hour soak test to the CI pipeline for the feed handler.
```

### 5. Deployment Strategies

**Why Trading Uses Conservative Deployment**

Most tech companies deploy to production multiple times per day. Trading firms deploy rarely and carefully. Reasons:
- Downtime during market hours has immediate financial cost
- A bug in the order path can send bad orders and cause regulatory issues
- Trading systems are deeply stateful (open orders, positions, P&L)
- Rollback is complex because state may have changed (you cannot un-execute a trade)

**Deployment Strategies**

```
Strategy       Description                     Trading Use
──────────────────────────────────────────────────────────────────────
Blue-Green     Two identical environments.      Common for stateless
               Switch traffic atomically.       services. Hard for
               Roll back by switching back.     stateful systems.

Canary         Deploy to a small % of          Most common for
               instances. Monitor. Expand       trading. Start with
               gradually.                       non-critical instruments.

Rolling        Update instances one at a        Used for large
               time. Each must pass health      clusters. Must handle
               check before proceeding.         mixed versions.

Off-hours      Deploy outside trading hours.    Standard for hot-path
               Full regression test before      components. Deploy at
               market open.                     night, test pre-market.
```

**Trading-Specific Deployment Practices**

1. **Deploy outside market hours**: Hot-path components (feed handlers, strategy engines, order gateways) are deployed outside trading hours. The deployment includes a full pre-market checkout:
   - All connections established
   - Market data flowing and books building correctly
   - Test orders sent to exchange simulation
   - Position reconciliation with previous session
   - Risk limits loaded and verified

2. **Canary by instrument**: Instead of canary by instance, run the new version on a subset of instruments. If ES (E-mini S&P) works correctly, expand to other products.

3. **Feature flags**: Deploy the code change but gate it behind a flag. Enable the flag during market hours only after confirming the deployment is stable.

4. **Companion testing**: Run the new version alongside the old version, both receiving the same market data, but only the old version sends orders. Compare the new version's decisions against the old version's actual results.

### 6. Capacity Planning

**Why Capacity Planning Matters in Trading**

Market events cause dramatic load spikes. FOMC announcements, Non-Farm Payrolls, and unexpected geopolitical events can increase message rates 5-10x above normal. A system that handles normal load but fails during spikes will fail at exactly the worst time -- when markets are most volatile and trading opportunities are largest.

**Throughput Modeling**

```
Component         Normal Load        Peak Load (5x)     Design Capacity
──────────────────────────────────────────────────────────────────────────
Market data       1M msg/sec          5M msg/sec         10M msg/sec
Order gateway     10K orders/sec      50K orders/sec     100K orders/sec
Risk engine       10K checks/sec      50K checks/sec     100K checks/sec
Book builder      500K updates/sec    2.5M updates/sec   5M updates/sec
```

Design for 2x peak load (10x normal). This gives headroom for unexpected events and system degradation.

**Load Testing**

Regular load testing (at least monthly) using captured production traffic replayed at elevated speeds:

1. **Baseline**: Record a typical trading day's market data and order flow.
2. **Amplify**: Replay at 2x, 5x, 10x normal speed.
3. **Measure**: At what multiplier does latency degrade? What is the first bottleneck?
4. **Stress**: Push to failure. Know your limits before the market tests them for you.

**Market Event Preparation**

Before scheduled market events (FOMC, NFP, earnings season for equities):
- Review capacity headroom
- Pre-scale any elastic components
- Verify all monitoring and alerting is operational
- Confirm incident response team is available
- Pre-position risk limits (tighter limits during volatile periods)
- Test kill switch functionality

**Capacity Metrics to Track**

```
Metric                              Warning Threshold    Critical
──────────────────────────────────────────────────────────────────
CPU utilization (hot-path core)     60%                  80%
NIC ring buffer utilization         50%                  70%
Memory utilization                  70%                  85%
Market data queue depth             50% of buffer        80% of buffer
Order queue depth                   50% of buffer        80% of buffer
Connection pool utilization         70%                  90%
```

### Summary: The Production Excellence Checklist

```
Monitoring:
  [ ] USE metrics for every resource on the hot path
  [ ] RED metrics for every service boundary
  [ ] Trading-specific SLIs (order latency, fill rate, data freshness)
  [ ] Dashboard showing real-time system health

Alerting:
  [ ] Symptom-based alerts with runbooks
  [ ] Severity levels mapped to response times
  [ ] Alert fatigue review process (monthly)
  [ ] Separate informational vs actionable alerts

Incident Response:
  [ ] Defined severity levels with response time targets
  [ ] Kill switch tested and accessible
  [ ] Failover procedures documented and tested
  [ ] Blameless postmortem process

Deployment:
  [ ] Hot-path deployments outside market hours only
  [ ] Pre-market checkout procedure
  [ ] Canary/staged rollout with automated health gates
  [ ] Rollback procedure tested (< 30 sec)

Capacity:
  [ ] Designed for 2x peak (10x normal) load
  [ ] Monthly load testing
  [ ] Market event preparation checklist
  [ ] Capacity metrics with warning/critical thresholds
```

---

## Practice Questions (20-30 min)

1. **You are designing the monitoring system for Jump's futures execution pipeline. What are the 5 most critical metrics you would track and what SLOs would you set?**

2. **An alert fires: "Order latency p99 > 50us" during market hours. Walk through your triage and mitigation process step by step.**

3. **Your team has 20 active alerts. 15 of them fire multiple times per week without requiring action. How do you fix this?**

4. **Design a pre-market checkout procedure for a trading system after a code deployment.** What checks do you run? In what order? What is the go/no-go decision?

5. **FOMC announcement is scheduled for tomorrow. What preparation steps do you take today?**

6. **A postmortem reveals that an incident lasted 10 minutes longer than necessary because the on-call engineer did not know how to trigger the kill switch. What systemic changes do you propose?**

7. **Your trading system handles normal load fine, but during the market open (9:30 AM), latency spikes by 5x for the first 2 minutes. How do you investigate and fix this?**

8. **Compare blue-green deployment and canary deployment for a trading order gateway. Which do you prefer and why?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** In the USE method, what does "Saturation" measure?
- A) How much of the resource is being used
- B) How much work is waiting because the resource is busy
- C) How many errors the resource has encountered
- D) The maximum capacity of the resource

**Q2.** Which is the best primary alert for a trading system?
- A) CPU utilization > 80%
- B) Order latency p99 > SLO threshold
- C) Disk usage > 70%
- D) GC pause duration > 5ms

**Q3.** What is the main purpose of a blameless postmortem?
- A) To avoid holding anyone accountable
- B) To identify systemic issues and prevent recurrence, without discouraging honest reporting
- C) To document the incident for regulatory compliance
- D) To determine which individual caused the incident

**Q4.** During a trading system incident, what should be prioritized first?
- A) Finding the root cause
- B) Mitigating the impact (stopping the bleeding)
- C) Writing the postmortem
- D) Notifying all stakeholders

**Q5.** Why do trading firms typically deploy hot-path components outside market hours?
- A) Developers are not available during market hours
- B) Deployment during market hours risks downtime or degraded performance when trading revenue is at stake
- C) Exchange rules prohibit deployments during trading
- D) It is easier to test at night

**Q6.** What is an error budget in the context of SLOs?
- A) The maximum number of errors allowed per day
- B) The amount of unreliability allowed before deployments are frozen, derived from the SLO target
- C) The budget allocated for fixing errors
- D) The time allocated for error investigation

**Q7.** For capacity planning, what multiplier over normal load should a trading system be designed to handle?
- A) 1.5x normal
- B) 2x normal (equal to peak)
- C) 2x peak (roughly 10x normal)
- D) 100x normal

**Q8.** Which deployment strategy allows instant rollback by switching a single pointer/load balancer?
- A) Rolling deployment
- B) Canary deployment
- C) Blue-green deployment
- D) Feature flag deployment

### Short Answer

**Q9.** Explain the difference between the USE method and the RED method. When would you use each?

**Q10.** Why is "alert on symptoms, not causes" the correct approach? Give an example of a symptom-based alert and a cause-based alert for a trading system.

**Q11.** Describe the "5 Whys" technique and apply it to this incident: "A trading strategy sent an order at a price 10% away from the market."

**Q12.** What is "companion testing" in the context of trading system deployment, and why is it safer than canary deployment for the order path?

**Q13.** Your SLO for order latency p99 is 20us. Last month, the actual p99 was 18us. A product manager wants to deploy a new feature that adds 3us of latency to the hot path. What do you recommend?

**Q14.** Why is market-hours uptime a more meaningful SLO than 24/7 uptime for a trading system?

**Q15.** Describe how you would load test a market data feed handler. What data do you use? What do you measure? How do you know you have found the bottleneck?

**Q16.** A new engineer asks "why do we need a kill switch if we have risk limits?" Explain the difference and why both are necessary.

---

## Quiz Answer Key

**Q1.** B) How much work is waiting because the resource is busy. Saturation indicates demand exceeding capacity. High saturation means requests are queuing, which directly increases latency. Examples: CPU run queue length, NIC receive ring buffer fullness, disk I/O wait queue.

**Q2.** B) Order latency p99 > SLO threshold. This is a symptom-based alert that directly measures what matters: whether the system is meeting its performance contract. CPU utilization is a cause metric -- high CPU is fine if latency is fine. Disk usage and GC pauses are contributing factors, not primary indicators.

**Q3.** B) To identify systemic issues and prevent recurrence, without discouraging honest reporting. If people fear blame, they hide information, making it harder to find root causes. Blameless postmortems create psychological safety for honest analysis. Note: "blameless" does not mean "accountable-less" -- teams are still accountable for implementing action items.

**Q4.** B) Mitigating the impact (stopping the bleeding). During a trading-hours incident, every second of degradation has financial cost. Trigger failover, kill switch, or rollback FIRST. Root cause analysis can wait until the system is stable. "Fix it now, understand it later."

**Q5.** B) Deployment during market hours risks downtime or degraded performance when trading revenue is at stake. Even a brief restart (seconds) can cause missed trading opportunities. A deployment that introduces a bug during market hours can cause bad orders or missed fills. Deploying outside market hours gives a window for testing and validation before markets open.

**Q6.** B) The amount of unreliability allowed before deployments are frozen, derived from the SLO target. If your SLO is 99.99% uptime (~4.3 min/month), your error budget is 4.3 minutes of downtime per month. When consumed, freeze non-critical changes and focus on reliability. This makes the reliability vs velocity trade-off explicit and data-driven.

**Q7.** C) 2x peak (roughly 10x normal). Trading load is spiky -- market events can cause 5-10x normal message rates. Designing for 2x peak gives headroom even during extreme events. Designing only for peak means you have zero margin, and any unexpected spike causes failure.

**Q8.** C) Blue-green deployment. With two identical environments, rollback is simply switching the traffic pointer back to the old (blue) environment. It is instant because the old environment is still running. Canary requires rolling back the canary instances, which is fast but not instant.

**Q9.** USE (Utilization, Saturation, Errors) is for infrastructure resources -- CPU, memory, network, disk. It answers "is this resource the bottleneck?" RED (Rate, Errors, Duration) is for services and request flows. It answers "is this service behaving correctly?" Use RED as your primary monitoring (detect problems from the user/consumer perspective) and USE for diagnosis (find the resource constraint causing the problem).

**Q10.** Alerting on causes generates false positives. CPU at 90% might be normal for a busy-polling trading system -- it does not mean anything is wrong. Symptom-based alert: "Order latency p99 > 20us" -- this directly measures whether the system is meeting its SLO. Cause-based alert: "CPU > 80%" -- this might or might not indicate a problem. You end up ignoring cause-based alerts because they often do not correspond to actual issues, which is the definition of alert fatigue.

**Q11.** 5 Whys:
1. Why did the strategy send an order at a bad price? The strategy used a stale best-offer price.
2. Why was the price stale? The book builder had not processed the latest market data update.
3. Why was the book builder behind? A market data gap caused the book builder to buffer messages while waiting for gap recovery.
4. Why was the book stale flag not checked? The strategy reads the book but does not check the "stale" flag before generating signals.
5. Why is there no check? The stale flag was added recently and the strategy was not updated to use it.
Action: Add a mandatory stale-book check in the strategy framework, enforced at the API level so individual strategies cannot skip it.

**Q12.** Companion testing runs the new version of the software alongside the production version. Both receive identical market data and signals, but only the production version sends real orders. The new version's decisions are logged and compared against the production version's actual results. It is safer than canary deployment for the order path because the new version never sends real orders -- there is zero risk of bad orders from the new code. Canary deployment does send real orders from the new version, which carries risk even if limited to a small subset.

**Q13.** The feature would push p99 from 18us to ~21us, exceeding the 20us SLO. Recommendations: (1) Investigate whether the 3us can be reduced through optimization (e.g., move the computation off the hot path, pre-compute, cache). (2) If 3us is unavoidable, discuss with stakeholders whether to raise the SLO to 25us (with justification for why the feature's value exceeds the latency cost). (3) If the SLO cannot change, the feature cannot be deployed on the hot path in its current form. The SLO exists precisely to prevent incremental latency creep.

**Q14.** Trading systems only generate revenue during market hours. Downtime at 3 AM on a Saturday has zero business impact (for equities -- futures are different since they trade ~23 hours). A 24/7 SLO dilutes the signal: a system could be down for an hour on Sunday and still meet 99.99% over the week, but 1 minute down during the market open would be catastrophic. Market-hours SLO focuses the reliability budget where it matters. Note: for futures, the "market hours" window is much wider (~23 hours for CME), making the SLO more stringent in absolute terms.

**Q15.** Load testing a feed handler: (1) Capture a full day of production market data (pcap file from the network). (2) Replay the pcap at 1x speed and record baseline latency percentiles. (3) Replay at 2x, 5x, 10x speed. At each level, record: p50/p99/p999 decode latency, CPU utilization, NIC ring buffer drops, memory usage, gap detection rate. (4) The bottleneck is the first resource that saturates: if CPU hits 100% first, the bottleneck is decode processing. If NIC ring buffer drops increase first, the bottleneck is packet reception. If memory grows unboundedly, there is a leak. (5) The system's capacity limit is the highest replay speed at which p99 latency stays below the SLO.

**Q16.** Risk limits prevent INDIVIDUAL bad orders (e.g., rejecting an order that exceeds the position limit). They operate on a per-order basis and handle known risk categories. A kill switch stops ALL order submission instantly. It is needed for scenarios that risk limits do not cover: (1) The risk system itself is malfunctioning (e.g., using stale limits). (2) The algorithm is sending many orders that individually pass risk checks but collectively are dangerous (e.g., submitting 1000 valid orders per second when normal is 10). (3) A systemic issue where continuing to participate in the market is dangerous regardless of individual order validity. Risk limits are the seatbelt; the kill switch is the emergency brake.
