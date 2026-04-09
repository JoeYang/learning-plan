# Day 11 (Sun Apr 19) -- System Design Mock Problems

## Overview (5 min)

System design interviews at trading firms differ from Big Tech interviews. They care less about "design Twitter" and more about "design a system that processes 10 million messages per second with sub-microsecond latency." The problems are deeper, more technically specific, and they expect you to discuss hardware, networking, and failure modes -- not just boxes and arrows. Today you work through three full design problems, each directly relevant to your Goldman Sachs experience and the Jump Trading role. Practice the 5-step framework until it becomes automatic.

---

## Reading Materials (60-90 min)

### The 5-Step System Design Framework

Every system design answer should follow this structure. Timing is for a 35-40 minute design session:

```
Step 1: Clarify Requirements     (2 min)   "Let me make sure I understand..."
Step 2: High-Level Architecture  (5 min)   Boxes, arrows, data flow
Step 3: Deep Dive Components     (15 min)  2-3 most critical components
Step 4: Trade-offs & Failures    (10 min)  What breaks? How do we handle it?
Step 5: Optimization & Scaling   (5 min)   Performance, monitoring, evolution
```

**Step 1: Clarify Requirements**

Ask 3-5 targeted questions. For trading systems, always clarify:
- Latency requirements (microseconds? milliseconds?)
- Throughput (messages per second? instruments?)
- Reliability (can we lose data? what is the blast radius of failure?)
- Scope (single venue or multi-venue? single region or global?)

**Step 2: High-Level Architecture**

Draw the major components and data flow. Use clear labels. Start from the external systems (exchange, clients) and work inward. Do not go into detail yet -- this is the map.

**Step 3: Deep Dive**

Pick 2-3 components that are technically interesting or critical to the requirements. Go deep: data structures, algorithms, protocol details, threading model, memory layout.

The interviewer may redirect you -- follow their lead. If they want to talk about the component you glossed over, pivot gracefully.

**Step 4: Trade-offs & Failures**

For each deep-dive component, discuss:
- What happens when it fails?
- How do you detect the failure?
- How do you recover?
- What are the trade-offs in your design? What did you optimize for and what did you sacrifice?

**Step 5: Optimization & Scaling**

How would you improve the system? Common directions:
- Performance optimization (caching, pre-computation, better data structures)
- Scalability (horizontal vs vertical, sharding)
- Monitoring and observability (what metrics matter?)
- Evolution (how would the system change if requirements doubled?)

---

### Problem 1: Market Data Distribution System

**Scenario**: Design a system that receives multicast market data from exchanges, normalizes it, builds order books, and distributes the data to N internal consumers (trading strategies, risk systems, surveillance).

#### Step 1: Clarify Requirements

Questions to ask:
- How many exchanges / feeds? (e.g., 10 exchanges, 50 multicast groups)
- How many instruments? (e.g., 10,000 futures contracts)
- What is the peak message rate? (e.g., 5 million messages/second aggregate)
- What is the latency requirement? (wire-to-consumer < 5 microseconds)
- How many consumers? (e.g., 20 strategy instances, 5 risk systems)
- Can consumers tolerate data loss? (strategies: no; surveillance: brief gaps OK)
- What is the recovery strategy for packet loss?

#### Step 2: High-Level Architecture

```
  Exchange A          Exchange B          Exchange C
  (Multicast)         (Multicast)         (Multicast)
      |                   |                   |
      v                   v                   v
+-------------+   +-------------+   +-------------+
| Feed Handler|   | Feed Handler|   | Feed Handler|
| (decode,    |   | (decode,    |   | (decode,    |
|  normalize, |   |  normalize, |   |  normalize, |
|  gap detect)|   |  gap detect)|   |  gap detect)|
+------+------+   +------+------+   +------+------+
       |                 |                 |
       +--------+--------+--------+--------+
                |                 |
        +-------v-------+ +------v--------+
        | Book Builder  | | Book Builder  |
        | (Instrument   | | (Instrument   |
        |  Group 1)     | |  Group 2)     |
        +-------+-------+ +------+--------+
                |                 |
        +-------v-----------------v--------+
        |     Distribution Layer           |
        |  (shared memory / IPC)           |
        +--+-----+-----+-----+-----+------+
           |     |     |     |     |
           v     v     v     v     v
         Strat  Strat  Risk  Risk  Surv
          1      2     Mgr   Mon   eillance
```

#### Step 3: Deep Dive

**Feed Handler Deep Dive**

Each feed handler runs on a dedicated core with kernel bypass (ef_vi or DPDK). It:

1. **Receives UDP multicast packets** via busy polling on the NIC.
2. **Line arbitration**: Subscribes to both A and B feed lines. Processes whichever arrives first per sequence number. Discards duplicates.
3. **Gap detection**: Maintains expected next sequence number per feed. On gap detection:
   - Buffer subsequent messages (they may arrive out of order within a small window).
   - Check if the redundant feed has the missing message.
   - If not recovered within N microseconds, request TCP retransmission from exchange recovery server.
   - If TCP recovery fails or is too slow, request a full instrument snapshot.
4. **Decode**: Parse exchange-specific wire format (SBE for CME, ITCH for ASX).
5. **Normalize**: Convert to internal `NormalizedUpdate` struct with fixed-point prices, internal instrument IDs, and both exchange and local timestamps.

```
Feed Handler Memory Layout (per feed):

+------------------+
| Sequence Tracker |  expected_seq[feed_id] -> uint64_t
+------------------+
| Gap Buffer       |  ring buffer of out-of-order messages
+------------------+
| Decode Buffer    |  pre-allocated buffer for raw packet
+------------------+
| Output Buffer    |  normalized messages, written to shared memory
+------------------+
```

**Book Builder Deep Dive**

Maintains a full limit order book per instrument. For an order-based feed:

```cpp
struct OrderBook {
    // Price levels indexed by tick offset from reference price
    PriceLevel bid_levels[MAX_TICKS];
    PriceLevel ask_levels[MAX_TICKS];
    
    int best_bid_tick;  // cached for O(1) BBO access
    int best_ask_tick;
    
    // Order lookup for cancel/modify
    // Open-addressing hash map: order_id -> (tick, side, qty)
    FlatHashMap<uint64_t, OrderInfo> orders;
};
```

Operations:
- **Add**: Insert order into hash map, update price level quantity, update best bid/ask if needed. O(1).
- **Cancel**: Lookup order in hash map, decrement price level quantity, update best bid/ask if level becomes empty. O(1).
- **Trade**: Same as cancel but also records the trade for downstream consumers.

**Distribution Layer Deep Dive**

The distribution layer must deliver book updates to N consumers with minimal added latency and without the consumers interfering with each other (a slow consumer must not block a fast one).

Options:
1. **Shared memory with sequence numbers**: Book builder writes updates to a shared memory ring buffer. Each consumer reads at its own pace. If a consumer falls behind and the buffer wraps, it detects the gap via sequence numbers and requests a snapshot.

2. **Multicast (internal)**: Use kernel bypass multicast within the data center. Same pattern as exchange feeds but on the internal network.

3. **Per-consumer memory-mapped files**: Each consumer maps the same file. Book builder writes; consumers read. OS handles page caching.

Recommended: Shared memory ring buffer for lowest latency.

```
Shared Memory Ring Buffer:
+---+---+---+---+---+---+---+---+---+---+
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |  <- slots
+---+---+---+---+---+---+---+---+---+---+
          ^               ^
          |               |
       Consumer A      Producer
       (reading)       (writing)

Each slot: [sequence_number | timestamp | instrument_id | update_data]
Consumer checks sequence number to detect gaps.
No locks. Producer writes, consumers read.
```

#### Step 4: Trade-offs & Failures

**Packet Loss**
- Redundant feeds (A/B line arbitration) handle most loss.
- TCP recovery handles the rest but adds 100us+ of latency.
- During recovery, the book is marked stale -- strategies should not trade on stale books.

**Feed Handler Crash**
- Run a standby feed handler in warm standby (receiving data but not publishing).
- On primary crash detection (missed heartbeat), standby takes over.
- Brief data gap during switchover -- consumers must handle.

**Slow Consumer (Backpressure)**
- Ring buffer design: slow consumers simply fall behind. The buffer overwrites old data.
- Consumer detects the gap and requests a book snapshot to catch up.
- Critical: a slow consumer NEVER blocks the producer or other consumers.

**Clock Skew**
- PTP synchronization on all machines.
- Include both exchange timestamp and local receive timestamp in each message.
- Monitor clock drift; alert if > 1us.

#### Step 5: Optimization

- **NUMA awareness**: Pin feed handlers to the NUMA node closest to the NIC.
- **Huge pages**: Use 2MB huge pages for shared memory to reduce TLB misses.
- **Instrument sharding**: Partition instruments across book builders by exchange segment to parallelize without sharing state.
- **Monitoring**: Track per-feed gap rate, per-instrument update rate, end-to-end latency percentiles, consumer lag.

---

### Problem 2: FIX Protocol Certification Testing Framework

**Scenario**: Design a testing framework that certifies FIX protocol implementations against exchange specifications. It should simulate an exchange, run scenario-based tests, support regression testing, and integrate with CI. You built this at Goldman -- frame it as "here is how I would design it again with what I know now."

#### Step 1: Clarify Requirements

Questions to ask:
- How many exchange protocols to support? (e.g., 10-15 exchanges, each with a different FIX dialect)
- What types of scenarios? (happy path, error handling, edge cases, performance)
- How fast should the test suite run? (< 5 minutes for CI, < 30 seconds for individual tests)
- Do we need to test session-level behavior (logon, logout, heartbeat, sequence number recovery)?
- Do we need performance/latency testing in addition to functional testing?

#### Step 2: High-Level Architecture

```
+------------------------------------------------------------------+
|                    Test Framework                                  |
|                                                                    |
|  +------------------+     +-------------------+                    |
|  | Test Definitions |     | Exchange Profiles |                    |
|  | (YAML/JSON)      |     | (FIX dialect      |                    |
|  |                  |     |  per exchange)     |                    |
|  +--------+---------+     +--------+----------+                    |
|           |                        |                               |
|  +--------v------------------------v----------+                    |
|  |           Test Runner / Orchestrator        |                    |
|  |  - loads test scenario                      |                    |
|  |  - configures simulated exchange            |                    |
|  |  - executes test steps                      |                    |
|  |  - validates assertions                     |                    |
|  +--------+-----------------------------------+                    |
|           |                                                        |
|  +--------v-----------------------------------+                    |
|  |         Simulated Exchange                  |                    |
|  |  +------------------+  +----------------+   |                    |
|  |  | FIX Engine       |  | Matching Engine|   |                    |
|  |  | (session mgmt,   |  | (price-time    |   |                    |
|  |  |  seq numbers)    |  |  priority)     |   |                    |
|  |  +------------------+  +----------------+   |                    |
|  |  +------------------+  +----------------+   |                    |
|  |  | Behavior Scripts |  | State Machine  |   |                    |
|  |  | (inject delays,  |  | (order lifecycle|  |                    |
|  |  |  errors, rejects)|  |  tracking)     |   |                    |
|  |  +------------------+  +----------------+   |                    |
|  +---------------------------------------------+                    |
|           |                                                        |
|  +--------v-----------------------------------+                    |
|  |     System Under Test (Gateway)             |                    |
|  |     (connects via FIX to simulated exch)    |                    |
|  +---------------------------------------------+                    |
+------------------------------------------------------------------+
           |
    +------v------+     +------------------+
    | CI Pipeline |     | Report Generator |
    | (Jenkins/   |     | (pass/fail,      |
    |  GitHub     |     |  latency stats,  |
    |  Actions)   |     |  coverage)       |
    +-------------+     +------------------+
```

#### Step 3: Deep Dive

**Simulated Exchange**

The simulated exchange is the core component. It must be configurable to behave like different real exchanges:

```yaml
# Exchange profile: CME
exchange_profile:
  name: CME
  fix_version: "FIX.4.2"
  session:
    heartbeat_interval: 30
    logon_requires_password: true
    supports_reset_on_logon: true
  order_handling:
    supported_order_types: [LIMIT, MARKET, IOC, FOK, GTC]
    self_trade_prevention: CANCEL_RESTING
    max_order_rate: 1000  # per second
    ack_delay_us: 50      # simulated processing delay
  error_behavior:
    reject_codes:
      unknown_instrument: 99
      insufficient_margin: 103
```

The behavior scripting layer allows tests to inject specific behaviors:

```yaml
# Test: Gateway handles reject correctly
test: order_reject_handling
steps:
  - action: connect
    assert: logon_successful
  
  - action: send_new_order
    params:
      symbol: "ESH6"
      side: BUY
      qty: 10
      price: 4500.00
      order_type: LIMIT
    
  - action: exchange_behavior
    inject: reject_order
    params:
      reject_reason: "insufficient_margin"
      reject_code: 103
    
  - assert: gateway_receives_reject
    expect:
      msg_type: "8"  # ExecutionReport
      ord_status: "8"  # Rejected
      text_contains: "insufficient_margin"
  
  - assert: gateway_state
    expect:
      order_count: 0  # order cleaned up internally
      position: 0     # no position from rejected order
```

**Test Categories**

```
Category              Examples                           Priority
────────────────────────────────────────────────────────────────────
Session Lifecycle     Logon, logout, heartbeat,          Critical
                      sequence recovery, forced logout
Order Lifecycle       New, ack, fill, partial fill,      Critical
                      cancel, replace, reject
Error Handling        Invalid fields, unknown symbols,    Critical
                      rate limit exceeded, session drop
Edge Cases            Cancel-replace race condition,      High
                      fill during cancel, duplicate       
                      order IDs, sequence number wrap
Performance           Order throughput, latency under     Medium
                      load, burst handling
Recovery              Reconnect after disconnect,         Critical
                      message replay, gap fill
```

**State Machine Validation**

The framework tracks the order state machine and validates that the system under test maintains correct state:

```
For each order, assert:
  - State transitions follow the valid state machine
  - No impossible transitions (e.g., FILLED -> NEW)
  - Position changes match fill reports
  - Sequence numbers are strictly increasing
  - Timestamps are monotonically increasing
```

#### Step 4: Trade-offs & Failures

**Fidelity vs Speed**: A high-fidelity simulation (including network delays, partial fills, concurrent events) is slower but catches more bugs. A fast simulation skips delays but may miss timing-related bugs. Solution: two modes -- "fast" for CI (skip delays) and "realistic" for pre-production (include delays).

**Protocol Coverage**: Exchanges update their FIX specifications regularly. The framework must be easy to update -- hence the YAML-based exchange profiles rather than hard-coded behavior.

**Determinism**: Tests must be deterministic -- same input always produces same output. Avoid real timers; use simulated time. Avoid real network; use in-process or loopback connections.

#### Step 5: Optimization

- **Parallel test execution**: Tests that use different simulated exchanges can run in parallel.
- **Coverage tracking**: Measure which FIX message types and fields have been tested. Highlight untested paths.
- **Regression detection**: Track test execution time. Alert if a test becomes slower (might indicate a performance regression in the gateway).
- **Snapshot testing**: Record the full FIX message exchange for passing tests. Diff against the snapshot on subsequent runs to detect unintended behavioral changes.

---

### Problem 3: Global Service Configuration Deployment System

**Scenario**: Design a system to manage configuration for hundreds of services across multiple regions. It must support validation, dry-run, staged rollout, and instant rollback. You built this at Goldman -- frame it from your experience.

#### Step 1: Clarify Requirements

Questions to ask:
- How many services / instances? (e.g., 500 services, 5000 instances across 5 regions)
- How often do configs change? (e.g., 50-100 changes per day)
- What is the blast radius tolerance? (a bad config should not take down all regions)
- How quickly must rollback happen? (< 30 seconds)
- Who makes config changes? (developers, SREs, automated systems)
- What types of config? (feature flags, connection strings, tuning parameters, routing rules)

#### Step 2: High-Level Architecture

```
+------------------------------------------------------------------+
|                     Config Management                              |
|                                                                    |
|  +------------------+     +-------------------+                    |
|  | Config Store     |     | Change Request    |                    |
|  | (Git repo or     |     | (PR / approval    |                    |
|  |  versioned DB)   |     |  workflow)         |                    |
|  +--------+---------+     +--------+----------+                    |
|           |                        |                               |
|  +--------v------------------------v----------+                    |
|  |           Config Pipeline                   |                    |
|  |                                             |                    |
|  |  1. Validate (schema, constraints)          |                    |
|  |  2. Dry-run (simulate deployment)           |                    |
|  |  3. Stage 1: Canary (1 instance per region) |                    |
|  |  4. Stage 2: Region 1 (25%)                 |                    |
|  |  5. Stage 3: Region 2 (50%)                 |                    |
|  |  6. Stage 4: All regions (100%)             |                    |
|  |                                             |                    |
|  |  [HALT + ROLLBACK at any stage]             |                    |
|  +--------+-----------------------------------+                    |
|           |                                                        |
+------------------------------------------------------------------+
            |
   +--------v---------+--------+---------+--------+---------+
   |                   |                  |                   |
+--v--+          +-----v----+      +-----v----+       +-----v----+
| NY  |          | London   |      | Tokyo    |       | Sydney   |
+--+--+          +----+-----+      +----+-----+       +----+-----+
   |                  |                 |                    |
   v                  v                 v                    v
+------+          +------+         +------+            +------+
|Config|          |Config|         |Config|            |Config|
|Agent |          |Agent |         |Agent |            |Agent |
|(each |          |(each |         |(each |            |(each |
| svc) |          | svc) |         | svc) |            | svc) |
+------+          +------+         +------+            +------+
```

#### Step 3: Deep Dive

**Config Store**

Use a Git repository as the source of truth. Every config change is a commit. This provides:
- Full audit trail (who changed what, when, why)
- Easy rollback (revert to any previous commit)
- Branching for testing (change configs on a branch, validate, then merge)
- Code review workflow (PRs for config changes)

Directory structure:
```
config-repo/
  schemas/
    trading-gateway.schema.json
    risk-engine.schema.json
  services/
    trading-gateway/
      base.yaml          # shared across all environments
      overrides/
        prod-ny.yaml     # region-specific overrides
        prod-london.yaml
        prod-tokyo.yaml
        prod-sydney.yaml
    risk-engine/
      base.yaml
      overrides/
        ...
  policies/
    rollout-policy.yaml  # staged rollout rules
    validation-rules.yaml
```

Config resolution: `base.yaml` merged with region-specific `overrides/*.yaml`. Overrides take precedence.

**Validation**

Multi-layer validation before any deployment:

```
Layer 1: Schema validation
  - JSON Schema / YAML schema
  - Type checking (string, int, bool, enum)
  - Required fields present
  - No unknown fields

Layer 2: Constraint validation
  - Value ranges (e.g., max_position_limit > 0, < 1000000)
  - Cross-field consistency (e.g., if feature_x_enabled, then feature_x_config must exist)
  - Cross-service consistency (e.g., gateway timeout < upstream service timeout)

Layer 3: Semantic validation
  - Connection strings resolve to valid endpoints
  - Referenced instruments/exchanges exist
  - Rate limits are within exchange-allowed bounds

Layer 4: Dry-run
  - Start the service with new config in a sandbox
  - Verify it initializes without errors
  - Run health checks
  - Compare behavior against baseline (diff of metrics, logs)
```

**Staged Rollout**

```
Stage     Scope              Duration    Gate
──────────────────────────────────────────────────────────
Canary    1 instance/region  10 min      Auto: error rate < 0.1%
                                         Auto: latency p99 < 2x baseline
Wave 1    25% of instances   30 min      Auto: same criteria
Wave 2    50% of instances   30 min      Manual approval for trading
Wave 3    100% of instances  -           Monitoring for 1 hour
```

At each stage gate:
- Automated health checks compare the canary/wave metrics against the baseline.
- If any metric degrades beyond threshold, automatically halt and rollback.
- For trading-critical services, require manual approval between waves.

**Rollback**

Rollback must be instant and reliable:
1. Every config agent caches the last known good config locally.
2. On rollback signal, agents immediately revert to cached config.
3. Rollback signal propagated via a separate control plane (not the same path as config distribution) for resilience.
4. Time to rollback: < 5 seconds to propagate signal, < 30 seconds for all services to reload.

```
Config Agent on Each Service:
+----------------------------------+
|  Current Config  | Previous Config|
|  (active)        | (cached)       |
+--------+---------+--------+------+
         |                  |
    On update:          On rollback:
    Previous = Current  Current = Previous
    Current = New       Reload service
    Reload service
+----------------------------------+
```

#### Step 4: Trade-offs & Failures

**Config Store Unavailable**
- Agents cache the current config locally. Services continue running with the last known config.
- No new deployments possible, but existing services are unaffected.

**Bad Config Passes Validation**
- This is why staged rollout exists. Canary catches most issues before broad deployment.
- Monitoring gates catch behavioral regressions that validation cannot.
- Manual approval gate for trading-critical services adds human judgment.

**Network Partition Between Regions**
- Each region has a local config cache/replica.
- If a region is partitioned, it continues with its current config.
- Config updates resume when connectivity is restored.
- Risk: regions running different config versions temporarily. Mitigated by version tagging and monitoring.

**Rollback Cascade**
- Rolling back one service's config might require rolling back dependent services.
- The system must model service dependencies and offer "coordinated rollback" for service groups.

#### Step 5: Optimization

- **Config diffing**: Show exactly what changed between versions. Human-readable diffs for review.
- **Impact analysis**: Before deployment, show which services and regions are affected.
- **Automated testing**: After config change, run integration tests against the affected services.
- **Emergency override**: Allow authorized users to push config changes bypassing staged rollout (with audit trail and post-hoc review).
- **Metrics**: Track time-to-deploy, rollback frequency, validation failure rate, mean time to detect bad config.

---

## Practice Questions (20-30 min)

1. **You are designing a market data distribution system and a consumer is consistently falling behind. How do you handle this without affecting other consumers?** Discuss backpressure strategies.

2. **In your FIX testing framework, how do you test the scenario where a cancel request and a fill arrive simultaneously?** Describe the test setup and assertions.

3. **Your config deployment system needs to support "dark launching" -- deploying a config change that is invisible to production traffic but can be tested. How would you implement this?**

4. **Walk through the failure modes of a shared-memory-based market data distribution layer.** What happens if the producer crashes? What if a consumer crashes? What if shared memory is corrupted?

5. **In the config system, how do you handle the chicken-and-egg problem: the config system itself needs configuration to run. How do you bootstrap it?**

6. **You need to add a new exchange feed to your market data system. Describe the process from protocol specification to production deployment.**

7. **An interviewer asks: "Your FIX testing framework uses YAML to define test scenarios. Why not just write tests in code?" Defend your design choice and acknowledge its limitations.**

8. **Design the monitoring dashboard for the market data distribution system.** What are the 5 most important metrics? What alerts would you set?

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** In a market data distribution system, what is the best strategy for handling a slow consumer?
- A) Block the producer until the consumer catches up
- B) Drop the slow consumer's connection
- C) Let the consumer fall behind on a ring buffer and detect/recover gaps via sequence numbers
- D) Duplicate all data to a separate buffer for slow consumers

**Q2.** What is the primary advantage of using a Git repository as the config store?
- A) Faster read performance than a database
- B) Built-in versioning, audit trail, and code review workflow
- C) Better availability than a distributed database
- D) Simpler schema validation

**Q3.** In the FIX testing framework, why should tests use simulated time rather than real time?
- A) Simulated time is faster
- B) Simulated time ensures deterministic, reproducible test results
- C) Real time is not available in CI environments
- D) Simulated time uses less memory

**Q4.** What is "line arbitration" in the context of market data feeds?
- A) Choosing between TCP and UDP
- B) Processing redundant A/B feed lines and using whichever delivers each message first
- C) Prioritizing one exchange's data over another
- D) Load balancing across multiple feed handlers

**Q5.** In a staged config rollout, what is the purpose of the canary stage?
- A) To test the config in a development environment
- B) To validate the config on a small subset of production before broad deployment
- C) To generate documentation for the config change
- D) To back up the previous config

**Q6.** When designing a simulated exchange for testing, which is more important for test reliability?
- A) Realistic latency simulation
- B) High message throughput
- C) Deterministic behavior for reproducible tests
- D) Support for multiple simultaneous connections

**Q7.** In the market data system, why is shared memory preferred over TCP for distributing data to co-located consumers?
- A) Shared memory is more reliable
- B) Shared memory avoids kernel network stack overhead and data copying
- C) Shared memory supports more consumers
- D) Shared memory is easier to implement

### Short Answer

**Q8.** Explain why a ring buffer is preferred over a queue for the market data distribution layer. What happens when the ring buffer wraps around?

**Q9.** In the config deployment system, describe the difference between "validation" and "dry-run." Why do you need both?

**Q10.** Your market data system processes 5 million messages per second. Each message is 64 bytes. What is the bandwidth requirement? Is this feasible on a 10 Gbps network link?

**Q11.** In the FIX testing framework, how would you test sequence number recovery after a simulated connection drop?

**Q12.** Describe a scenario where a config change passes all automated validation but still causes a production issue. How does the staged rollout catch this?

**Q13.** Why does the config rollback mechanism use a separate control plane from the config distribution path?

**Q14.** In the market data system, what is the trade-off between maintaining one book builder per instrument vs one book builder per exchange?

**Q15.** How would you measure the end-to-end latency of the market data distribution system, from exchange multicast packet to consumer receiving the update?

---

## Quiz Answer Key

**Q1.** C) Let the consumer fall behind on a ring buffer and detect/recover gaps via sequence numbers. This ensures the producer and fast consumers are never blocked. The slow consumer recovers by requesting a book snapshot when it detects it has fallen behind.

**Q2.** B) Built-in versioning, audit trail, and code review workflow. Git provides commit history (who changed what, when), branching (test changes in isolation), and pull request workflow (peer review before deployment). These are critical for config management in a trading environment.

**Q3.** B) Simulated time ensures deterministic, reproducible test results. Real time introduces non-determinism -- a test that passes with a 50ms heartbeat timeout might fail intermittently if the system is under load. Simulated time eliminates this flakiness.

**Q4.** B) Processing redundant A/B feed lines and using whichever delivers each message first. Exchanges provide redundant feeds on separate network paths. Line arbitration deduplicates by sequence number and takes the faster delivery, improving both latency and reliability.

**Q5.** B) To validate the config on a small subset of production before broad deployment. The canary stage exposes the new config to real production traffic on a small scale. If it causes problems, the blast radius is limited to one instance per region.

**Q6.** C) Deterministic behavior for reproducible tests. If tests produce different results on different runs, they are useless for regression testing. Determinism (via simulated time, controlled message ordering, no real I/O) is the foundation of reliable testing.

**Q7.** B) Shared memory avoids kernel network stack overhead and data copying. With shared memory, data written by the producer is immediately visible to consumers without any system calls, context switches, or data copying. This is the lowest-latency IPC mechanism.

**Q8.** A ring buffer has fixed size and overwrites old data when it wraps. This is desirable because: (1) no dynamic memory allocation, (2) bounded memory usage, (3) a slow consumer simply misses old data rather than causing unbounded memory growth. When the ring wraps, the consumer detects a gap via sequence numbers and requests a full book snapshot to recover. A queue would grow without bound if a consumer falls behind, eventually exhausting memory.

**Q9.** Validation checks the config against static rules (schema, constraints, cross-references) without running any code. It is fast (milliseconds) and catches structural errors. Dry-run actually starts the service with the new config in a sandbox and verifies it initializes and passes health checks. It catches runtime errors that static validation cannot detect (e.g., a connection string that is syntactically valid but points to a non-existent host, or a combination of settings that causes a startup crash). You need both because validation is fast but shallow, while dry-run is thorough but slow.

**Q10.** 5,000,000 messages/sec * 64 bytes/message = 320,000,000 bytes/sec = 320 MB/s = 2.56 Gbps. This is feasible on a 10 Gbps link (25.6% utilization). However, this does not account for packet headers (UDP/IP/Ethernet adds ~42 bytes per packet) or bursts. With headers on individual packets: 5M * 106 bytes = 530 MB/s = 4.24 Gbps. Still feasible but approaching 50% utilization. Batching multiple messages per packet would reduce header overhead.

**Q11.** Test steps: (1) Establish FIX session, exchange a few messages so both sides have sequence numbers > 1. (2) Simulate a connection drop (close the TCP socket from the exchange side). (3) The system under test should detect the disconnection and attempt to reconnect. (4) On reconnect, it sends a Logon with its expected sequence numbers. (5) The simulated exchange sends a SequenceReset-GapFill for any messages the system missed. (6) Assert: the system correctly processes the gap fill, updates its internal state, and resumes normal operation with correct sequence numbers.

**Q12.** Example: A config change increases the max_concurrent_connections from 100 to 200. Validation confirms it is a valid integer within the allowed range. Dry-run starts the service successfully. But in production, the increased connection count causes the service to exhaust its file descriptor limit, leading to connection failures under load. The canary stage catches this because the canary instance, receiving real production traffic, hits the file descriptor limit and starts logging errors. The automated health check detects the elevated error rate and halts the rollout.

**Q13.** If the config distribution path is broken (which might be WHY you need to rollback -- a bad config broke connectivity), the rollback signal would not reach the agents. Using a separate control plane (e.g., a dedicated management network, SSH-based push, or out-of-band signaling) ensures rollback works even when the primary distribution path is degraded.

**Q14.** Per-instrument: Maximum parallelism (each instrument on its own core), no contention between instruments. But with 10,000 instruments, you need 10,000 cores, which is impractical. Per-exchange: Simple, one book builder handles all instruments from one exchange. But a burst of updates on one instrument delays processing of updates for other instruments on the same exchange. Best compromise: per-instrument-group (e.g., per exchange segment or product group), balancing parallelism with resource usage.

**Q15.** Use NIC hardware timestamps at both ends: (1) The feed handler records the NIC RX timestamp when the exchange packet arrives. (2) The distribution layer writes this timestamp into the shared memory message. (3) The consumer records the NIC or CPU timestamp when it reads the message from shared memory. End-to-end latency = consumer_read_time - nic_rx_time. For the shared memory segment, since there is no NIC involved, use rdtsc on both the writer and reader side (they are on the same machine, so the TSC is synchronized). Alternatively, use a hardware timestamping probe (e.g., Memory Fabric Tap) on the network to measure wire-to-wire without instrumenting the application.
