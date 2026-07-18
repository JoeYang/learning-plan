# Learning Plan: APAC Exchange Connectivity

**Start date:** 2026-02-28
**Target completion:** ~2026-03-28 (4 weeks + 1 day)
**Schedule:** 5 sessions/week, ~1.5 hours each (21 sessions)
**Status:** not-started

---

## Phase 1: Foundations — Architecture & C++ Reading Skills (Sessions 1-5)

### Session 1: Exchange Connectivity Architecture Overview
**Objective:** Map the full data flow from exchange to strategy and back — know every component and what it does
- [x] Draw the architecture: exchange → feedhandler → book builder → strategy → OMS → order gateway → exchange
- [x] Feedhandler role: receive multicast market data, parse binary protocols, normalize, publish internal events
- [x] Order gateway role: manage exchange sessions, send/receive orders, handle acks/fills/rejects
- [x] OMS role: order state tracking, position management, risk checks, reconciliation
- [x] Separation of concerns: why feedhandlers and order gateways are separate processes
- [x] Compare to CME MDP 3.0 experience: what's the same (binary parsing, sequence numbers, recovery) and what's new (ITCH vs SBE, OUCH vs iLink)
**Key concepts:** feedhandler, order gateway, OMS, book builder, multicast, unicast, co-location
**Resources:** Johnson "Algorithmic Trading and DMA" Ch. 10-11, team architecture diagrams

### Session 2: Protocol Landscape — FIX, SBE, ITCH, OUCH & Exchange-Specific
**Objective:** Build a reference table of all protocols you'll encounter and understand their design philosophy
- [x] FIX protocol: tag-value format, session layer (Logon/Heartbeat/Logout), application layer (NewOrderSingle, ExecutionReport)
- [x] Why FIX is slow: text parsing, delimiter scanning, field lookup overhead
- [x] Binary protocols motivation: fixed-size messages, zero-copy parsing, no delimiter scanning
- [x] SBE (Simple Binary Encoding): CME's approach — schema-driven, field offsets known at compile time
- [x] ITCH: exchange-disseminated market data — message-type byte + fixed fields, no request/response
- [x] OUCH: exchange order entry — lightweight binary, maps 1:1 to order lifecycle events
- [x] SoupBinTCP: transport framing for OUCH (length-prefixed, sequenced, heartbeat)
- [x] Build reference table: protocol × exchange × direction (market data vs order entry) × transport (multicast vs TCP)
- [x] Exchange-specific protocols that don't fit the pattern: HKEX OMD, HKEX OCG/OAPI
**Key concepts:** FIX, SBE, ITCH, OUCH, SoupBinTCP, binary protocol design, tag-value vs fixed-layout
**Resources:** FIX 4.2 spec (overview), NASDAQ ITCH 5.0 spec, OUCH 4.2 spec, SBE spec

### Session 3: C++ Reading — Templates, CRTP & Type Dispatch in Protocol Code
**Objective:** Read C++ template patterns used in production protocol code without getting lost
- [ ] Function templates: how feedhandlers dispatch on message type (template<typename MsgType> void process(const MsgType&))
- [ ] Class templates: parameterized protocol handlers (Handler<SGXConfig> vs Handler<JPXConfig>)
- [ ] CRTP (Curiously Recurring Template Pattern): static polymorphism for zero-overhead callbacks
  - Pattern: class MyHandler : public Handler<MyHandler> — derived class passed as template arg to base
  - Why: avoids virtual function call overhead on the hot path
- [ ] Tag dispatch and type traits: compile-time branching on message types
- [ ] constexpr and compile-time computation: protocol constants, field offsets, message sizes
- [ ] Read real examples: identify these patterns in open-source exchange connectivity code
**Key concepts:** CRTP, tag dispatch, static polymorphism, template specialization, compile-time dispatch
**Resources:** CppCon talks on CRTP, open-source protocol handler code, Vandevoorde "C++ Templates"

### Session 4: C++ Reading — Memory Layout, Buffers & Zero-Copy Parsing
**Objective:** Understand how feedhandlers parse binary messages without memory allocation
- [ ] Packed structs: #pragma pack(1) or __attribute__((packed)) — struct layout matches wire format
- [ ] reinterpret_cast: casting a byte buffer directly to a message struct pointer (zero-copy)
- [ ] Endianness: network byte order (big-endian) vs host (little-endian), ntohl/ntohs, __builtin_bswap
- [ ] Ring buffers for message passing: producer writes, consumer reads, no allocation on hot path
- [ ] Memory-mapped buffers: pre-allocated receive buffers, avoid malloc/new in the data path
- [ ] Alignment and padding: why packed structs can cause performance issues on some architectures
- [ ] Read real examples: trace how a raw UDP packet becomes a typed message struct
**Key concepts:** packed structs, zero-copy parsing, reinterpret_cast, endianness, ring buffers, alignment
**Resources:** Stacy Gaudreau HFT blog series, rigtorp/SPSCQueue, protocol parsing code

### Session 5: State Machines — Session, Order Lifecycle & Recovery
**Objective:** Understand the state machines that underpin all protocol code
- [ ] Session state machine: Disconnected → Connecting → LoggingIn → Active → Recovering → Disconnected
- [ ] Order lifecycle state machine: New → PendingAck → Accepted → PartialFill → Filled / Cancelled / Rejected
- [ ] Replace/cancel state machine: PendingReplace, PendingCancel — what happens when you cancel a pending replace?
- [ ] Recovery state machine: gap detected → request retransmit → buffering → replaying → back to normal
- [ ] State machine implementation patterns in C++: enum + switch, state pattern, transition tables
- [ ] Why state machines matter: every bug in exchange connectivity is a state machine bug
- [ ] Compare to CME MDP 3.0 recovery: instrument-level vs channel-level, snapshot polling vs request
**Key concepts:** session states, order states, recovery states, state transitions, gap detection
**Resources:** Exchange protocol specs (session management sections), team's state machine code

---

## Phase 2: Market Data — Feedhandler Design & Protocols (Sessions 6-10)

### Session 6: Feedhandler Architecture Deep Dive
**Objective:** Understand all the sub-components inside a feedhandler and how they interact
- [ ] Receive path: NIC → kernel → userspace buffer (or kernel bypass) → parser → book builder → publisher
- [ ] A/B feed arbitration: why exchanges send duplicate feeds, sequence-number-based dedup
  - Fast path: process whichever feed's message arrives first
  - Arbitration: track sequence numbers per feed, switch on gaps
- [ ] Multicast group management: joining/leaving groups, IGMP, per-product multicast addresses
- [ ] Message parsing pipeline: framing → message type dispatch → field extraction → event creation
- [ ] Book building: applying Add/Modify/Delete/Execute messages to maintain order book state
- [ ] Event publishing: how parsed market data gets to downstream consumers (shared memory, IPC, ring buffer)
- [ ] Instrument definition handling: reference data messages that define products, tick sizes, lot sizes
**Key concepts:** A/B arbitration, multicast, book building, event publishing, instrument definitions
**Resources:** Team feedhandler code, exchange multicast specs

### Session 7: ITCH Protocol Message-by-Message Walkthrough
**Objective:** Know every ITCH message type and how it maps to book operations — compare to CME MDP 3.0
- [ ] ITCH design philosophy: full depth, message-by-message, order-by-order (MBO), exchange broadcasts everything
- [ ] Core messages: AddOrder, OrderExecuted, OrderCancelled, OrderReplaced, OrderDeleted
- [ ] Trade messages: Trade (non-book), CrossTrade, BrokenTrade
- [ ] System messages: SystemEvent, StockDirectory, TradingAction, RegSHO
- [ ] Book building from ITCH: maintain order map (orderID → price/qty/side), apply modifications
- [ ] Sequence numbers and gap detection: per-stream sequences, what to do on a gap
- [ ] Compare to CME MDP 3.0:
  - MDP is MBP (market-by-price) with implied; ITCH is MBO (market-by-order)
  - MDP uses SBE encoding; ITCH uses fixed-layout messages
  - MDP has snapshots on a separate channel; ITCH recovery varies by exchange
- [ ] Rebuild a simple ITCH book from a message trace
**Key concepts:** MBO vs MBP, AddOrder, OrderExecuted, OrderCancelled, sequence numbers, gap detection
**Resources:** NASDAQ ITCH 5.0 specification (reference), SGX ITCH spec (for comparison)

### Session 8: SGX Titan ITCH — SGX-Specific Extensions & Products
**Objective:** Know SGX Titan ITCH specifics — what's different from vanilla ITCH, what products trade
- [ ] SGX Titan platform overview: derivatives exchange, electronic trading since Titan migration
- [ ] SGX ITCH vs NASDAQ ITCH: message type differences, field extensions, additional message types
- [ ] SGX-specific messages: combination orders, implied pricing, trade amendment/cancellation
- [ ] Products traded on SGX: Nikkei 225 futures, MSCI Taiwan, Iron Ore (TSI), China A50, USD/CNH
- [ ] Multicast channel structure: how SGX organizes products across multicast groups
- [ ] SGX recovery mechanism: snapshot request or retransmit request — how it works in practice
- [ ] Tick sizes, lot sizes, trading hours for key products (especially overlap with JPX for Nikkei arb)
- [ ] Read SGX ITCH spec: identify every field you'd need to parse for the key products
**Key concepts:** SGX Titan, SGX ITCH extensions, derivatives products, multicast structure, recovery
**Resources:** SGX Titan ITCH specification, SGX market data technical guide

### Session 9: JPX J-GATE & Arrowhead Market Data
**Objective:** Understand JPX's market data for both derivatives (OSE/J-GATE) and cash equity (TSE/arrowhead)
- [ ] JPX structure: TSE (cash equities, arrowhead platform) vs OSE (derivatives, J-GATE platform)
- [ ] J-GATE ITCH for OSE derivatives: how it differs from NASDAQ/SGX ITCH
- [ ] Key derivatives products: Nikkei 225 futures/options, TOPIX futures, JGB futures, mini contracts
- [ ] arrowhead market data for TSE cash: FLEX Full (full depth) vs FLEX Standard
- [ ] FLEX protocol: JPX's own binary protocol (not ITCH) — message structure, book update model
- [ ] Recovery mechanisms: J-GATE retransmit service, arrowhead snapshot
- [ ] JPX-specific considerations: trading hours (JST), pre-open/closing auctions, special quotes, daily limits
- [ ] Nikkei arbitrage context: SGX Nikkei vs JPX Nikkei — why both feeds matter
**Key concepts:** J-GATE, arrowhead, FLEX, OSE derivatives, TSE cash, Nikkei futures
**Resources:** JPX J-GATE ITCH specification, JPX arrowhead FLEX specification, JPX technical guides

### Session 10: HKEX OMD-D — A Different Approach to Market Data
**Objective:** Understand HKEX OMD-D — it's NOT ITCH, and knowing the differences is critical
- [ ] HKEX platform overview: derivatives (OMD-D) vs securities (OMD-C), Genium INET platform
- [ ] OMD-D protocol: HKEX's own binary format — NOT ITCH, NOT SBE
- [ ] Key difference: aggregate depth (MBP) not order-by-order (MBO) — you get price levels, not individual orders
- [ ] OMD-D message types: MarketDefinition, SeriesDefinition, AggregateOrderBookUpdate, Trade, etc.
- [ ] Refresh mechanism: OMD-D uses periodic full refreshes (snapshots) rather than retransmit-on-demand
- [ ] Line arbitration: similar concept to A/B feeds but HKEX calls them Line 1/Line 2
- [ ] Products: Hang Seng Index futures/options, H-shares, mini futures, stock options, commodities
- [ ] HKEX-specific: Volatility Control Mechanism (VCM), Closing Auction Session (CAS), pre-open
- [ ] Compare OMD-D to ITCH side-by-side: what a feedhandler must do differently
**Key concepts:** OMD-D, aggregate depth, MBP, refresh mechanism, line arbitration, Genium INET
**Resources:** HKEX OMD-D specification, HKEX market data technical reference

---

## Phase 3: Order Entry — Gateway Design & Protocols (Sessions 11-15)

### Session 11: Order Gateway Architecture
**Objective:** Understand the internal design of an order gateway and why it's more complex than a feedhandler
- [ ] Core responsibilities: session management, order routing, state tracking, risk checks, throttling
- [ ] Session management: login sequences, heartbeating, sequence number synchronization, reconnection
- [ ] Throttle management: exchange-imposed rate limits, how to implement without blocking
- [ ] Cancel-on-disconnect (COD): what happens when the TCP connection drops — exchange behavior varies
- [ ] Fail-safe mechanisms: kill switches, position limits, max order size, fat-finger checks
- [ ] Order state tracking: local order book mirrors exchange state, handles acks/fills/rejects
- [ ] Idempotency: ClOrdID/token management, preventing duplicate orders on reconnect
- [ ] Gateway vs feedhandler complexity: bidirectional vs unidirectional, state management, error recovery
**Key concepts:** session management, throttling, cancel-on-disconnect, fail-safe, idempotency, ClOrdID
**Resources:** Team order gateway code, exchange order entry specs (session management sections)

### Session 12: OUCH Protocol Walkthrough
**Objective:** Know the OUCH protocol end-to-end — from EnterOrder to Executed
- [ ] OUCH design philosophy: minimal, binary, one message per order event, no request/response correlation needed
- [ ] SoupBinTCP transport: length-prefix framing, login/logout, sequenced vs unsequenced, heartbeat
- [ ] Client → server messages: EnterOrder, ReplaceOrder, CancelOrder
- [ ] Server → client messages: Accepted, Replaced, Cancelled, Executed, Rejected, SystemEvent
- [ ] Order token: client-assigned, unique per session, how it maps to exchange order ID
- [ ] Message flow examples:
  - Simple fill: EnterOrder → Accepted → Executed
  - Replace: EnterOrder → Accepted → ReplaceOrder → Replaced → Executed
  - Cancel: EnterOrder → Accepted → CancelOrder → Cancelled
  - Reject: EnterOrder → Rejected (why: invalid price, throttle, risk)
- [ ] Compare to CME iLink: OUCH is simpler (no FIX session semantics), but less flexible
- [ ] Sequence number management: SoupBinTCP server sequences, gap handling on reconnect
**Key concepts:** OUCH, SoupBinTCP, EnterOrder, Accepted, Executed, order token, sequence numbers
**Resources:** OUCH 4.2 specification, SoupBinTCP specification

### Session 13: SGX Titan & JPX J-GATE OUCH Specifics
**Objective:** Know what's different about SGX and JPX OUCH vs vanilla OUCH
- [ ] SGX Titan OUCH: exchange-specific fields (account type, order book ID, customer info)
- [ ] SGX order types: limit, market-to-limit, stop-loss, combination orders
- [ ] SGX throttle policy: messages per second limit, what happens when exceeded (queue vs reject)
- [ ] SGX cancel-on-disconnect behavior: configurable per session, implications for strategy
- [ ] JPX J-GATE OUCH: OSE derivatives order entry, JPX-specific fields
- [ ] JPX order types: limit, market, stop, IOC, FAK (Fill and Kill), FOK (Fill or Kill)
- [ ] JPX throttle policy: how it differs from SGX, daily order limits
- [ ] JPX-specific: self-trade prevention, position limits, margin requirements
- [ ] Cross-exchange comparison: SGX OUCH vs JPX OUCH field-by-field for key message types
**Key concepts:** SGX OUCH extensions, JPX OUCH extensions, throttle policies, order types, COD
**Resources:** SGX Titan OUCH specification, JPX J-GATE OUCH specification

### Session 14: HKEX OCG & OAPI — A Different Protocol Family
**Objective:** Understand HKEX order entry — it's NOT OUCH, built on Genium INET / binary FIX
- [ ] HKEX OCG (Open Connectivity Gateway): derivatives order entry platform
- [ ] OCG protocol: Genium INET-based binary protocol — NOT OUCH, NOT standard FIX
- [ ] Session management: OCG login sequence, throttle limits, heartbeat, password management
- [ ] OAPI (Open API): the older HKEX API, some products still use it
- [ ] OCG message types: NewOrder, CancelOrder, MassCancel, ExecutionReport, OrderCancelReject
- [ ] HKEX-specific fields: broker ID, investor ID (BCAN for northbound), account type
- [ ] HKEX order types: limit, enhanced limit, special limit, at-auction, at-auction limit
- [ ] HKEX cancel-on-disconnect: how it works, differences from SGX/JPX
- [ ] Compare OCG to OUCH: message complexity, session management overhead, field richness
**Key concepts:** OCG, OAPI, Genium INET, HKEX order types, BCAN, broker ID
**Resources:** HKEX OCG specification, HKEX derivatives trading technical reference

### Session 15: C++ Reading — Networking & I/O Patterns
**Objective:** Understand the networking code patterns used in feedhandlers and order gateways
- [ ] Socket basics in C++: socket(), bind(), connect(), send(), recv() — the syscall layer
- [ ] Multicast: setsockopt(IP_ADD_MEMBERSHIP), receiving market data from multicast groups
- [ ] Non-blocking I/O: fcntl(O_NONBLOCK), why blocking I/O is unacceptable on the hot path
- [ ] Event loops: epoll (Linux), kqueue (macOS) — waiting for multiple sockets efficiently
- [ ] Busy-polling: spinning on recv() instead of sleeping — trades CPU for latency
- [ ] Kernel bypass overview: DPDK, Solarflare OpenOnload, Mellanox VMA — concept, not implementation
- [ ] TCP for order entry: Nagle's algorithm (TCP_NODELAY), send buffering, connection management
- [ ] UDP for market data: no flow control, no retransmit — why this is fine for multicast feeds
- [ ] Read real examples: identify these patterns in networking code
**Key concepts:** epoll, multicast, non-blocking I/O, busy-polling, kernel bypass, TCP_NODELAY
**Resources:** Stevens "Unix Network Programming", Beej's Guide, team networking code

---

## Phase 4: Integration, Operations & Synthesis (Sessions 16-21)

### Session 16: Low-Latency Anti-Patterns in Exchange Connectivity
**Objective:** Know the common mistakes that kill latency in feedhandlers and order gateways
- [ ] Sequence gap stalls: blocking the entire feed on a single gap instead of continuing and requesting retransmit
- [ ] Hot path allocation: any malloc/new in the parsing or order submission path
- [ ] Logging on the hot path: synchronous logging that blocks message processing
- [ ] Lock contention: mutexes in the data path, especially between feed and strategy threads
- [ ] Unnecessary copies: copying message data instead of passing pointers/references
- [ ] Ignoring throttle limits: sending orders faster than the exchange allows → connection drop
- [ ] Naive reconnection: reconnecting without re-syncing state → stale order state, duplicate orders
- [ ] String operations: string formatting, comparison, allocation in latency-sensitive code
- [ ] System call overhead: context switches from unnecessary syscalls in the hot path
- [ ] For each anti-pattern: what it looks like in code, why it's bad, what the fix is
**Key concepts:** hot path, allocation-free, zero-copy, lock-free, throttle compliance, state sync
**Resources:** CppCon low-latency talks, team code review feedback, production incident reports

### Session 17: Testing Exchange Connectivity
**Objective:** Know how exchange connectivity code is tested at every level
- [ ] Unit testing: message parsing, state machines, book building — test with crafted binary messages
- [ ] Pcap replay: capturing real exchange traffic, replaying through the feedhandler
- [ ] Simulated exchanges: mock exchange servers that speak the protocol, for order gateway testing
- [ ] Certification/conformance testing: exchange-provided test environments, required before going live
  - SGX certification process
  - JPX conformance testing
  - HKEX readiness testing
- [ ] Integration testing: full round-trip (send order, receive ack/fill) against test exchange
- [ ] Regression testing: replaying historical scenarios, especially around exchange outages and edge cases
- [ ] Performance testing: latency measurement, throughput testing, burst handling
- [ ] What to test that people forget: recovery paths, gap handling, session reconnect, throttle behavior
**Key concepts:** pcap replay, simulated exchange, certification, conformance, regression testing
**Resources:** Exchange certification guides, team testing infrastructure, pcap libraries (libpcap)

### Session 18: Debugging Tools & Packet Analysis
**Objective:** Get hands-on with the tools you'll actually use to debug exchange connectivity issues
- [ ] tcpdump basics: capturing packets on a specific interface and port
  - Capture multicast market data: `tcpdump -i eth0 -w capture.pcap udp and dst 239.x.x.x`
  - Capture TCP order entry: `tcpdump -i eth0 -w capture.pcap tcp and port 1234`
  - Useful flags: `-nn` (no DNS), `-X` (hex+ASCII), `-s 0` (full packet), `-c N` (count limit)
  - Capture filters vs display filters: BPF syntax for efficient capture
- [ ] Wireshark / tshark for pcap analysis:
  - Loading pcaps, filtering by protocol/port/IP, following TCP streams
  - Decoding binary protocol messages: custom dissectors vs raw hex inspection
  - Identifying sequence gaps: sorting by sequence number, spotting missing messages
  - Measuring inter-packet timing: delta time analysis for latency investigation
  - tshark for command-line analysis: `tshark -r capture.pcap -Y "tcp.port==1234" -T fields -e ...`
- [ ] Hex dump reading: mapping raw bytes to protocol message fields manually
  - Identifying message type byte, length prefix, field boundaries
  - Endianness in practice: reading multi-byte fields from hex dumps
  - Cross-referencing with protocol spec: field offset tables
- [ ] Common debugging scenarios:
  - "Feed went silent" — is the multicast arriving? (tcpdump confirms NIC-level receipt)
  - "Orders getting rejected" — capture and decode the reject message, read the reject reason
  - "Sequence gap won't close" — capture retransmit request/response, verify sequence numbers
  - "Latency spike" — pcap timestamps to pinpoint which hop is slow
  - "Login failing" — capture the handshake, compare to spec byte-by-byte
- [ ] Other useful tools:
  - netstat / ss: check socket state, multicast group membership, buffer sizes
  - ethtool: NIC stats, dropped packets, ring buffer sizes
  - strace: trace syscalls to see what the process is actually doing (recv, send, poll)
  - perf / flamegraph: CPU profiling to find hot spots in the parsing path
- [ ] Building a debugging checklist: systematic approach from "something is wrong" to root cause
**Key concepts:** tcpdump, Wireshark, tshark, pcap analysis, hex dump reading, BPF filters, strace
**Resources:** tcpdump man page, Wireshark docs, team pcap archives, exchange protocol specs (for field mapping)

### Session 19: Monitoring & Operational Readiness
**Objective:** Know how to monitor exchange connectivity in production and respond to issues
- [ ] Latency monitoring: tick-to-trade, feed-to-publish, order-to-ack — where to measure, what's normal
- [ ] Gap monitoring: sequence number gaps, gap frequency, gap duration — when to alert
- [ ] Throughput monitoring: messages per second, burst rates — capacity planning
- [ ] Position reconciliation: comparing internal positions to exchange-reported positions, end-of-day checks
- [ ] Exchange schedule awareness: market open/close times across APAC time zones, holidays, half-days
  - SGX: SGT (UTC+8), T session, T+1 session
  - JPX: JST (UTC+9), day session, night session
  - HKEX: HKT (UTC+8), morning session, afternoon session
- [ ] Runbook items: what to do when a feed goes down, when an order gateway disconnects, when a gap won't close
- [ ] Alerting: what to alert on (gaps, latency spikes, position mismatches, throttle hits, session drops)
- [ ] Post-incident: how to investigate connectivity issues, useful logs, pcap analysis
**Key concepts:** tick-to-trade latency, gap monitoring, position reconciliation, runbooks, APAC trading hours
**Resources:** Team monitoring dashboards, operational runbooks, exchange trading calendars

### Session 20: APAC Exchange Comparison Matrix & Multi-Exchange Architecture
**Objective:** Synthesize everything into a comparison framework and think about multi-exchange design
- [ ] Build the master comparison matrix:
  - Rows: SGX, JPX (OSE), JPX (TSE), HKEX
  - Columns: market data protocol, order entry protocol, book model (MBO/MBP), recovery mechanism, transport, throttle limits, COD behavior, key products, trading hours
- [ ] Multi-exchange architecture: how to handle multiple exchanges in one system
  - Common abstractions: exchange-agnostic order interface, normalized market data events
  - Exchange-specific adapters: protocol-specific parsers and gateways behind common interfaces
  - Configuration-driven: exchange parameters (throttle limits, tick sizes) as config, not code
- [ ] Latency considerations across exchanges: which exchange is fastest, co-location options
- [ ] Cross-exchange strategies: arbitrage (SGX vs JPX Nikkei), hedging across exchanges
- [ ] What to study next: deeper C++ (from the C++ Trading Systems plan), specific product knowledge, algo strategies
**Key concepts:** comparison matrix, multi-exchange architecture, exchange adapters, normalization
**Resources:** All previous session notes, exchange specs, team architecture docs

### Session 21: Capstone — Trace a Full Trade Lifecycle on SGX
**Objective:** Trace every step from an ITCH market data tick to an OUCH order fill on SGX Titan
- [ ] Set the scene: you see a price move on SGX Nikkei futures via the feedhandler
- [ ] Market data path: UDP multicast → NIC → feedhandler → ITCH parse → book update → price event published
- [ ] Strategy decision: price event triggers a signal → strategy decides to send a limit order
- [ ] Order path: strategy → OMS (risk checks, position check) → order gateway → OUCH EnterOrder → SoupBinTCP → TCP to SGX
- [ ] Exchange processing: SGX receives order → validates → inserts in book → sends Accepted back
- [ ] Fill path: a matching order arrives → SGX matches → sends Executed (OUCH) and Trade (ITCH)
- [ ] Gateway processes fill: Executed → update local order state → notify OMS → update position
- [ ] Feedhandler processes trade: Trade message → update book → publish trade event
- [ ] End-to-end: annotate latency at each hop, identify the critical path
- [ ] What could go wrong: gaps, rejects, partial fills, connection drops — and how each is handled
- [ ] Deliverable: a complete annotated diagram of the full lifecycle with protocol messages labeled
**Key concepts:** end-to-end trade lifecycle, critical path, latency budget, failure modes
**Resources:** All previous session notes, SGX ITCH + OUCH specs, team architecture diagrams
