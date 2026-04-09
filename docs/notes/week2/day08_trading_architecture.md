# Day 8 (Thu Apr 16) -- Trading System Architecture

## Overview (5 min)

Trading system architecture is the backbone of what Jump Trading builds and operates. As a Futures Execution Services engineer, you will work directly on the components that take a trading signal and turn it into an executed order on an exchange -- all within microseconds. This day covers the end-to-end pipeline: from the moment market data leaves an exchange to the moment your order confirmation arrives. Understanding how these components interact, where latency hides, and how failures propagate is arguably the most important knowledge for your interview.

Your Goldman Sachs experience building a simulated exchange gives you a rare advantage: you have touched most of these components firsthand. The goal today is to deepen that understanding, fill any gaps, and learn to articulate the design trade-offs at an interview-grade level.

---

## Reading Materials (60-90 min)

### 1. Market Data Feed Handler

The feed handler is the first component in any trading system. Its job is to receive raw market data from exchanges and transform it into a normalized, usable format for downstream consumers.

**UDP Multicast Reception**

Exchanges broadcast market data via UDP multicast because it is the most efficient way to deliver the same data to many participants simultaneously. Unlike TCP, there is no connection setup, no acknowledgment overhead, and no head-of-line blocking. The exchange sends each packet once to a multicast group address, and the network hardware replicates it to all subscribers.

```
Exchange ──UDP Multicast──> Switch ──> NIC ──> Kernel ──> Feed Handler
                              │
                              ├──> Firm A
                              ├──> Firm B
                              └──> Firm C
```

The feed handler typically binds to one or more multicast groups (e.g., one per product group or exchange segment). Each packet contains one or more messages with a sequence number. The sequence number is critical -- it is how you detect packet loss.

**Packet Loss and Gap Recovery**

UDP provides no delivery guarantee. Packets can be lost due to network congestion, NIC buffer overflows, or kernel drops. The feed handler must:

1. Track the expected next sequence number per feed.
2. Detect gaps immediately when a higher-than-expected sequence number arrives.
3. Initiate gap recovery -- typically via a TCP retransmission request to the exchange, or by switching to a secondary (redundant) feed that may have the missing data.

Gap recovery introduces latency. During the gap, the order book state is uncertain. A well-designed system will:
- Buffer out-of-order messages while waiting for the gap fill.
- Mark the book as "stale" or "uncertain" so downstream strategies do not trade on incomplete data.
- Apply the gap-filled messages in sequence order once received.
- Have a timeout after which the system requests a full book snapshot rather than individual gap fills.

**Normalization**

Every exchange has its own wire protocol (CME uses MDP 3.0 with SBE encoding, ASX uses ITCH, ICE uses iMpact). The feed handler translates these into a common internal representation. A normalized message might look like:

```
struct NormalizedUpdate {
    uint64_t timestamp_ns;     // exchange timestamp
    uint64_t recv_timestamp_ns; // local receipt time
    uint32_t instrument_id;     // internal instrument ID
    uint8_t  side;              // BID or ASK
    int64_t  price;             // price in fixed-point (e.g., ticks)
    uint32_t quantity;          // size at this price level
    uint8_t  update_type;       // ADD, MODIFY, DELETE, TRADE
    uint64_t order_id;          // exchange order ID (if order-based feed)
};
```

Using fixed-point integers for prices avoids floating-point comparison issues and is faster to process.

**Book Building**

From the normalized updates, the feed handler (or a separate book builder component) maintains a real-time limit order book for each instrument. There are two styles of market data feeds:

- **Order-based feeds** (e.g., ITCH): Every individual order is visible. You see each add, modify, cancel, and execution. The book builder maintains a map of order_id to (price, quantity, side) and reconstructs the book.
- **Level-based feeds** (e.g., CME MDP top-of-book or depth): You see aggregate quantity at each price level. Simpler to process but you lose individual order visibility.

The book builder outputs a complete order book snapshot that downstream consumers (strategies, risk systems) can query.

### 2. Order Book Data Structure

The limit order book (LOB) is the central data structure in any exchange or trading system. It represents all outstanding buy and sell orders for an instrument, organized by price and time.

**Structure**

```
         BIDS (buy orders)          |        ASKS (sell orders)
  Price    Qty    Orders             |  Price    Qty    Orders
  100.05   200   [O1:100, O3:100]   |  100.06   150   [O2:150]
  100.04   500   [O4:300, O5:200]   |  100.07   300   [O6:300]
  100.03   100   [O7:100]           |  100.08   250   [O8:100, O9:150]
```

The best bid is the highest buy price (100.05). The best ask is the lowest sell price (100.06). The difference is the spread (0.01).

**Implementation Choices**

For a matching engine (exchange side), you need fast operations:
- **Add order**: Insert at a price level, append to the time-priority queue at that level. O(1) if the price level exists, O(log N) if you need to find/create it.
- **Cancel order**: Remove a specific order by ID. Requires O(1) lookup by order_id (hash map) plus O(1) removal from the queue (doubly-linked list or mark-and-skip).
- **Execute/match**: Always against the best price level, always the oldest order at that level. O(1) access to best price, O(1) access to front of queue.

Common implementations:
- **Price levels**: A sorted map (red-black tree or skip list) keyed by price, or a fixed-size array indexed by price tick offset from a reference price (extremely fast for instruments with bounded price ranges).
- **Orders at each level**: A doubly-linked list (preserves insertion order = time priority, O(1) removal).
- **Order lookup**: A hash map from order_id to a pointer/iterator into the linked list.

For a trading firm's internal book (built from market data), the requirements are slightly different -- you mostly need fast reads (what is the best bid/ask? what is the depth at level N?) and fast updates (apply the next market data message).

### 3. Matching Engine

The matching engine is the heart of an exchange. It receives incoming orders and determines if they can be matched against existing resting orders in the book.

**Price-Time Priority**

The most common matching algorithm is price-time priority (also called FIFO):
1. An incoming buy order matches against the lowest-priced sell orders first.
2. At the same price level, orders are matched in the order they arrived (time priority).
3. An incoming sell order matches against the highest-priced buy orders first.

**Order Types**

| Type | Behavior |
|------|----------|
| **Limit** | Specifies a maximum buy price or minimum sell price. Rests in the book if not immediately matchable. |
| **Market** | Executes immediately at the best available price. No price limit. Dangerous in thin markets. |
| **IOC** (Immediate or Cancel) | Like a limit order but any unfilled portion is immediately cancelled. Never rests in the book. |
| **FOK** (Fill or Kill) | Must be filled entirely or not at all. If full quantity is not available at the limit price or better, the entire order is cancelled. |
| **GTC** (Good Till Cancel) | A limit order that remains in the book until explicitly cancelled or filled. |
| **Day** | Like GTC but automatically cancelled at end of trading day. |

**Matching Logic (Pseudocode)**

```
function match(incoming_order, book):
    opposite_side = book.asks if incoming_order.is_buy else book.bids

    while incoming_order.remaining_qty > 0:
        best_level = opposite_side.best()
        if best_level is None:
            break  // no liquidity
        if not price_matches(incoming_order, best_level):
            break  // price doesn't cross

        for resting_order in best_level.orders:
            fill_qty = min(incoming_order.remaining_qty, resting_order.remaining_qty)
            execute_trade(incoming_order, resting_order, fill_qty, best_level.price)
            if incoming_order.remaining_qty == 0:
                break

        if best_level.is_empty():
            opposite_side.remove_level(best_level)

    // Handle remaining quantity based on order type
    if incoming_order.remaining_qty > 0:
        if incoming_order.type in [MARKET, IOC, FOK]:
            cancel(incoming_order)
        elif incoming_order.type in [LIMIT, GTC, DAY]:
            book.add_resting(incoming_order)
```

**Why This Matters at Jump**

Jump operates on exchanges globally. Understanding matching engine behavior helps predict execution outcomes, design smarter order types, and identify edge cases (e.g., self-trade prevention, auction mechanisms, implied matching in futures spreads).

### 4. Order Management System (OMS)

The OMS tracks every order through its lifecycle and maintains the firm's position and P&L.

**Order Lifecycle State Machine**

```
                    +---> REJECTED
                    |
  NEW ──> PENDING_ACK ──> ACKNOWLEDGED ──> PARTIALLY_FILLED ──> FILLED
                    |           |                  |
                    |           +---> PENDING_CANCEL ──> CANCELLED
                    |           |
                    |           +---> PENDING_REPLACE ──> REPLACED
                    |
                    +---> EXPIRED
```

Key transitions:
- **NEW -> PENDING_ACK**: Order sent to exchange, awaiting acknowledgment.
- **PENDING_ACK -> ACKNOWLEDGED**: Exchange confirms the order is live in the book.
- **ACKNOWLEDGED -> PARTIALLY_FILLED**: Some quantity has been executed.
- **PARTIALLY_FILLED -> FILLED**: All quantity has been executed.
- **ACKNOWLEDGED -> PENDING_CANCEL**: Cancel request sent.
- **PENDING_CANCEL -> CANCELLED**: Exchange confirms cancellation.

**Race Conditions**

The most dangerous period is between sending an action and receiving confirmation. During PENDING_CANCEL, the order might still get filled. The OMS must handle "unsolicited fills" -- fills that arrive for orders that are in a pending-cancel state. This is normal, not an error.

**Position Tracking**

The OMS maintains real-time positions:
```
Position = sum of all fills (buys positive, sells negative)
Average Price = weighted average of fill prices
Realized P&L = sum of (exit_price - entry_price) * quantity for closed positions
Unrealized P&L = (current_market_price - average_entry_price) * open_position
```

Position tracking must be exactly consistent with exchange records. Any discrepancy (a "break") triggers immediate investigation.

### 5. Smart Order Router (SOR)

For instruments listed on multiple venues (common in equities and increasingly in futures), the SOR decides where to send each order.

**Routing Decisions**

```
Strategy Signal: "Buy 500 contracts"
         |
    Smart Order Router
    /        |        \
 Venue A   Venue B   Venue C
 Ask: 100  Ask: 99   Ask: 100
 Qty: 200  Qty: 300  Qty: 400
```

The SOR considers:
- **Best price**: Route to the venue with the best price.
- **Available liquidity**: If you need 500 and venue B only has 300 at the best price, split across venues.
- **Fees**: Different venues charge different maker/taker fees. A slightly worse price at a cheaper venue might result in a better net cost.
- **Latency**: If venue A is 2us away and venue C is 50us away, you might prefer venue A to reduce adverse selection risk.
- **Fill probability**: Historical fill rates at each venue.

**Venue-specific behavior**: Some venues offer rebates for providing liquidity (maker-taker model). The SOR might choose to post passive orders on rebate venues and take liquidity on inverted venues.

### 6. Risk Management

Pre-trade risk checks are the last line of defense before an order reaches the exchange. They must be extremely fast (sub-microsecond in HFT) because they sit on the critical path.

**Pre-Trade Checks**

| Check | Purpose |
|-------|---------|
| **Position limits** | Prevent exceeding maximum position per instrument or portfolio |
| **Notional limits** | Cap the total dollar value of outstanding orders + positions |
| **Rate limits** | Limit orders per second to prevent runaway algorithms |
| **Fat finger checks** | Reject orders with unreasonable price (e.g., > 5% from last trade) or size |
| **Credit limits** | Ensure the firm has sufficient margin/capital for the order |
| **Self-trade prevention** | Prevent the firm's buy orders from matching against its own sell orders |

**Implementation Considerations**

Risk checks must be on the hot path but must not add significant latency. Common approaches:
- Pre-compute limits and cache them in memory (no database lookups on the hot path).
- Use atomic operations for position/count updates to avoid locks.
- Implement as a simple sequential check pipeline -- each check is a single comparison.
- Kill switch: a single flag that instantly disables all order submission if set.

**Real-Time P&L**

Risk systems also compute real-time P&L using mark-to-market prices from the feed handler. This enables:
- Loss limits: automatically flatten positions if losses exceed thresholds.
- Drawdown monitoring: track peak-to-trough P&L within a trading session.
- Exposure monitoring: net and gross exposure across all instruments.

### 7. Execution Gateway

The execution gateway translates between the firm's internal order representation and the exchange's native protocol.

**FIX Protocol**

FIX (Financial Information eXchange) is the industry standard for order entry. Key messages:

| Tag | Message | Direction |
|-----|---------|-----------|
| 35=D | New Order Single | Firm -> Exchange |
| 35=8 | Execution Report | Exchange -> Firm |
| 35=F | Order Cancel Request | Firm -> Exchange |
| 35=G | Order Cancel/Replace | Firm -> Exchange |
| 35=0 | Heartbeat | Both |
| 35=A | Logon | Both |

**Session Management**

FIX sessions use sequence numbers to ensure message delivery:
- Each side maintains an outgoing sequence number that increments with every message.
- On reconnection, the sides exchange sequence numbers and perform gap fill for any missed messages.
- This is similar to TCP's sequence numbers but at the application layer.

**Native Protocols**

For latency-sensitive trading, many exchanges offer native binary protocols that are faster than FIX (less parsing overhead, smaller message size). Examples: CME iLink, ASX OUCH. The gateway must support both.

**Failover**

The gateway must handle:
- Exchange disconnections: automatic reconnect with session recovery.
- Primary/secondary exchange gateways: seamless switchover.
- Order state reconciliation: after reconnection, verify all order states match.

### Putting It All Together

```
+------------------+     +------------------+     +------------------+
|   Exchange A     |     |   Exchange B     |     |   Exchange C     |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
    UDP Multicast            UDP Multicast            UDP Multicast
         |                        |                        |
+--------v---------+     +--------v---------+     +--------v---------+
|  Feed Handler A  |     |  Feed Handler B  |     |  Feed Handler C  |
|  (decode, norm)  |     |  (decode, norm)  |     |  (decode, norm)  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         +----------+-------------+----------+-------------+
                    |                        |
            +-------v--------+       +-------v--------+
            |  Book Builder  |       |  Book Builder  |
            |  (instrument1) |       |  (instrument2) |
            +-------+--------+       +-------+--------+
                    |                        |
            +-------v------------------------v--------+
            |         Trading Strategy                 |
            |  (signal generation, alpha model)        |
            +-------+---------------------------------+
                    |
            +-------v--------+
            |  Risk Manager  |
            |  (pre-trade)   |
            +-------+--------+
                    |
            +-------v--------+
            |  Smart Order   |
            |  Router        |
            +---+----+---+---+
                |    |   |
         +------+  +-+   +------+
         |         |            |
  +------v---+ +---v------+ +--v-------+
  | Gateway A| | Gateway B| | Gateway C|
  | (FIX)    | | (native) | | (FIX)    |
  +------+---+ +---+------+ +--+-------+
         |         |            |
    Exchange A  Exchange B  Exchange C
```

**Latency Budget Example (Futures HFT)**

```
Component                  Typical Latency
─────────────────────────────────────────
NIC receive (kernel bypass)    0.5 us
Feed decode + normalize        0.3 us
Book update                    0.1 us
Strategy decision              0.5 us
Risk check                     0.2 us
Order encode                   0.2 us
NIC transmit                   0.5 us
─────────────────────────────────────────
Total (wire-to-wire)          ~2-3 us
Network one-way (co-lo)       ~1-5 us
```

Every microsecond matters. This is why each component is optimized independently and why architectural decisions (single-threaded vs multi-threaded, kernel bypass, memory layout) have such outsized impact.

---

## Practice Questions (20-30 min)

Write out answers to these as if explaining to an interviewer:

1. **Walk me through what happens from the moment an exchange publishes a market data update to the moment your trading system has an updated order book.** Cover each component, the data transformations, and where latency is introduced.

2. **You detect a gap in the market data sequence numbers. What do you do?** Describe your gap recovery strategy, how you handle the uncertain period, and what happens if gap recovery fails.

3. **Explain the trade-offs between an order-based feed and a level-based feed.** When would you prefer each? How does the choice affect your book builder's complexity and accuracy?

4. **Design the data structure for a limit order book that supports add, cancel, and match operations. What are the time complexities?** Draw out the structure and explain your choices.

5. **An order is in PENDING_CANCEL state and a fill arrives. What happens?** Walk through the OMS state machine and explain how the system handles this race condition.

6. **How would you implement pre-trade risk checks without adding measurable latency to the order path?** Discuss data structures, caching, and computation strategies.

7. **Your FIX gateway disconnects from the exchange mid-session. Describe the reconnection and recovery process.** Cover sequence number reconciliation, gap fill, and order state verification.

8. **Compare your Goldman simulated exchange to a production exchange.** What simplifications did you make? What would you need to add for production readiness?

9. **Why do most high-frequency trading systems prefer UDP multicast for market data instead of TCP?** What are the downsides and how do you mitigate them?

10. **A trader reports that their order was filled at a worse price than the market data showed at the time. What are the possible explanations?** Walk through the debugging process.

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** In a price-time priority matching engine, which order gets filled first?
- A) The largest order at the best price
- B) The most recent order at the best price
- C) The oldest order at the best price
- D) Orders are filled randomly at the best price

**Q2.** What is the primary reason exchanges use UDP multicast for market data distribution?
- A) UDP is more reliable than TCP
- B) UDP multicast efficiently delivers the same data to many receivers without per-connection overhead
- C) UDP has built-in gap recovery
- D) UDP packets are smaller than TCP packets

**Q3.** An IOC (Immediate or Cancel) order with a limit price of 100 is sent to an exchange where the best ask is 101. What happens?
- A) The order rests in the book at price 100
- B) The order is immediately cancelled with no fill
- C) The order is filled at 101
- D) The order waits for the price to reach 100

**Q4.** Which data structure combination is most appropriate for a high-performance limit order book?
- A) Binary search tree for price levels + array for orders at each level
- B) Hash map for price levels + stack for orders at each level
- C) Sorted map/array for price levels + doubly-linked list for orders + hash map for order lookup
- D) Priority queue for all orders regardless of price level

**Q5.** In FIX protocol, what is the purpose of sequence numbers?
- A) To prioritize messages by importance
- B) To detect missing messages and enable gap fill recovery
- C) To encrypt message contents
- D) To measure network latency

**Q6.** A FOK (Fill or Kill) order for 500 contracts arrives. The book has 300 contracts at the best price and 400 at the next level. What happens?
- A) 300 contracts are filled at the best price, 200 at the next level
- B) 300 contracts are filled, 200 are cancelled
- C) The entire order is cancelled because 500 is not available at a single price level
- D) The entire order is filled: 300 at the best price and 200 at the next level

**Q7.** What is the "spread" in an order book?
- A) The total number of orders in the book
- B) The difference between the best ask and best bid price
- C) The total quantity available at the best price
- D) The difference between the highest and lowest prices in the book

**Q8.** Which pre-trade risk check is specifically designed to prevent algorithmic errors from sending orders at absurd prices?
- A) Position limits
- B) Rate limits
- C) Fat finger checks
- D) Credit limits

### Short Answer

**Q9.** Explain why a trading system's OMS must handle "unsolicited fills" -- fills that arrive after a cancel request has been sent but before the cancel is confirmed.

**Q10.** What is the difference between "wire-to-wire latency" and "application latency" in a trading system? Why does the distinction matter?

**Q11.** Describe two strategies for handling market data packet loss and the trade-off between them.

**Q12.** Why do high-performance trading systems use fixed-point integer arithmetic for prices instead of floating-point?

**Q13.** In a smart order router, why might you route an order to a venue with a slightly worse price? Give two reasons.

**Q14.** What is "self-trade prevention" and why do exchanges implement it?

**Q15.** Explain the concept of a "kill switch" in a trading risk system. When would it be triggered and what does it do?

**Q16.** You are building a feed handler that processes CME market data. The feed provides redundant A and B lines with the same data. How would you use both feeds to minimize packet loss?

**Q17.** What happens to GTC orders at the end of a trading session on most futures exchanges? How does this differ from equity markets?

---

## Quiz Answer Key

**Q1.** C) The oldest order at the best price. Price-time priority means best price first, then first-in-first-out at each price level.

**Q2.** B) UDP multicast efficiently delivers the same data to many receivers without per-connection overhead. The exchange sends one packet, and network infrastructure replicates it. TCP would require a separate connection (and bandwidth) per subscriber.

**Q3.** B) The order is immediately cancelled with no fill. An IOC order requires immediate execution. Since the limit price (100) does not cross the best ask (101), no match is possible, and the IOC is cancelled.

**Q4.** C) Sorted map/array for price levels + doubly-linked list for orders + hash map for order lookup. The sorted structure enables O(1) best-price access, doubly-linked lists preserve time priority and allow O(1) removal, and the hash map enables O(1) order lookup by ID for cancellations.

**Q5.** B) To detect missing messages and enable gap fill recovery. Each side increments its outgoing sequence number. If the receiver sees a gap, it knows messages were lost and can request retransmission.

**Q6.** D) The entire order is filled: 300 at the best price and 200 at the next level. FOK requires the FULL quantity to be fillable (not necessarily at a single price level). Since 300 + 400 = 700 > 500, the full quantity is available, so it fills across levels. If total available were less than 500, the entire order would be cancelled.

**Q7.** B) The difference between the best ask and best bid price. The spread is a key indicator of market liquidity -- tighter spreads indicate more liquid markets.

**Q8.** C) Fat finger checks. These validate that the order price is within a reasonable range of the current market price and that the order size is not unreasonably large.

**Q9.** Between sending a cancel request and receiving confirmation, the order is still live on the exchange and can be matched. The OMS must accept these fills even though a cancel was requested. Ignoring them would create a position discrepancy between the firm's records and the exchange's records. The OMS transitions from PENDING_CANCEL back to PARTIALLY_FILLED (or FILLED), and then may re-issue the cancel for any remaining quantity.

**Q10.** Wire-to-wire latency measures the time from when a market data packet arrives at the NIC to when the resulting order packet leaves the NIC. Application latency measures only the time spent in userspace code (feed handler, strategy, risk check, order encode). The difference is kernel/driver overhead plus NIC processing time. Wire-to-wire is the true competitive metric because it includes all overhead that affects when your order actually arrives at the exchange.

**Q11.** Strategy 1: **Redundant feeds** -- subscribe to both A and B feed lines and take the first copy received, using the other to fill gaps. Low latency but requires double the network bandwidth. Strategy 2: **TCP gap fill request** -- request retransmission from the exchange's recovery server. Higher latency (round-trip to recovery server) but uses less bandwidth. Trade-off: redundant feeds recover faster but cost more infrastructure; TCP recovery is simpler but slower.

**Q12.** Floating-point arithmetic introduces rounding errors that can cause price comparisons to fail (e.g., 0.1 + 0.2 != 0.3). In trading, exact price matching is essential -- a one-tick error could mean the difference between getting a fill and not. Fixed-point integers (e.g., representing $100.05 as 10005) allow exact arithmetic and faster comparisons. They also avoid the overhead of floating-point unit exceptions and denormalized numbers.

**Q13.** (1) **Lower fees**: A venue might charge lower exchange fees or offer a rebate that more than compensates for the slightly worse price. (2) **Lower latency**: A closer venue (in terms of network latency) reduces adverse selection risk -- the faster your order arrives, the less likely the price has moved against you.

**Q14.** Self-trade prevention (STP) prevents a firm's buy order from matching against its own sell order on the exchange. Exchanges implement it because self-trades can be used for wash trading (artificially inflating volume), which is illegal market manipulation. STP rules vary by exchange -- some cancel the resting order, some cancel the incoming order, and some cancel both.

**Q15.** A kill switch is a mechanism that instantly halts all order submission from a trading system. It is typically a single boolean flag checked on the hot path before any order is sent. It would be triggered by: runaway P&L losses exceeding a threshold, an algorithm sending orders at an abnormal rate, detection of a system malfunction (e.g., stale market data being treated as live), or manual activation by a risk manager. When triggered, it cancels all outstanding orders and prevents new ones from being sent.

**Q16.** Subscribe to both A and B feed lines simultaneously. For each message, use the sequence number to deduplicate -- process whichever copy arrives first, discard the duplicate. If you detect a gap on one feed, the other feed may already have (or soon deliver) the missing message. Only fall back to TCP gap fill if both feeds have the gap. This approach is called "line arbitration" and gives you near-perfect data availability with minimal added latency.

**Q17.** On most futures exchanges, GTC orders actually persist across trading sessions -- they remain active until explicitly cancelled or filled (or until the contract expires). This differs from equity markets where many exchanges cancel GTC orders after a set number of days (e.g., 90 days) or at the end of each session depending on the venue's rules. The OMS must track these long-lived orders and reconcile them at each session open.
