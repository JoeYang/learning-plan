# Day 3 (Sat Apr 11) — Networking Fundamentals

## Overview (5 min)

Networking is arguably the most critical domain knowledge for a Futures Execution Services role. Every trade flows over a network — market data arrives via multicast UDP, orders go out over TCP (often FIX protocol), and the entire system lives or dies by its ability to handle network events with minimal latency. Jump Trading operates at the bleeding edge of network performance, using techniques like kernel bypass, FPGA-based network cards, and co-location to shave microseconds. Understanding networking from the OSI model down to socket-level programming and latency optimization is non-negotiable.

---

## Reading Materials (60-90 min)

### 1. OSI Model & TCP/IP Stack

The OSI model has 7 layers, but in practice the TCP/IP model (4 layers) is what matters:

```
OSI Layer        TCP/IP Layer     Protocol Examples       Trading Relevance
---------------------------------------------------------------------------
7. Application   Application      FIX, HTTP, DNS          FIX protocol for orders
6. Presentation  Application      TLS, compression        Encryption of order flow
5. Session        Application      FIX session layer       Session management
4. Transport     Transport        TCP, UDP                TCP for orders, UDP for mkt data
3. Network       Internet         IP, ICMP, IGMP          Routing, multicast group mgmt
2. Data Link     Network Access   Ethernet, ARP           Switches, MAC addresses
1. Physical      Network Access   Fiber, copper           Co-location, direct feeds
```

**Why this matters:** When debugging a trading system, you need to know which layer a problem lives at. A FIX sequence number gap is an application layer issue. A TCP retransmission is transport layer. A switch port flapping is data link. Each requires different tools (Wireshark vs. tcpdump vs. ethtool).

### 2. TCP Deep Dive

TCP provides reliable, ordered, byte-stream delivery over an unreliable network. It's the backbone of order entry in trading.

#### Three-Way Handshake

Establishing a TCP connection requires three packets:

```
Client                        Server
  |--- SYN (seq=x) ------------>|
  |<-- SYN-ACK (seq=y, ack=x+1)|
  |--- ACK (seq=x+1, ack=y+1)->|
  |     Connection Established   |
```

1. **SYN**: Client picks a random initial sequence number (ISN) x and sends SYN
2. **SYN-ACK**: Server picks its ISN y, acknowledges the client's SYN (ack=x+1)
3. **ACK**: Client acknowledges the server's SYN (ack=y+1)

**Latency impact:** The handshake takes 1.5 RTTs before data can flow. For a co-located system (RTT < 1ms), this is negligible at connection time. But if connections are established frequently (e.g., reconnecting after a failure), it adds up. This is why persistent connections matter.

#### Flow Control

TCP uses a **sliding window** mechanism. The receiver advertises its **receive window** (rwnd) — how many bytes it can accept. The sender never sends more than rwnd unacknowledged bytes.

```
Sender perspective:
[sent, ACKed] [sent, not ACKed] [can send] [cannot send yet]
              |<--- in-flight --->|<- window ->|
```

If the receiver's application is slow to read data, rwnd shrinks, and the sender slows down. This is **back-pressure** — the network naturally throttles the sender to match the receiver's capacity.

**Trading relevance:** If your order router sends faster than the exchange can process, the exchange's TCP window closes and your sends block. This can cause order latency spikes. Monitoring TCP window sizes with `ss -i` helps diagnose this.

#### Congestion Control

Separate from flow control, congestion control prevents the sender from overwhelming the network itself. Key algorithms:

- **Slow Start**: Start with a small congestion window (cwnd), double it every RTT until a threshold is reached
- **Congestion Avoidance**: After the threshold, grow cwnd linearly (additive increase)
- **Fast Retransmit**: If 3 duplicate ACKs are received, retransmit the missing segment immediately (don't wait for timeout)
- **Fast Recovery**: After fast retransmit, halve cwnd (multiplicative decrease) instead of resetting to 1

Modern servers often use **CUBIC** (Linux default) or **BBR** (Google's algorithm). For co-located trading, congestion control rarely kicks in because the network path is short with abundant bandwidth.

#### Nagle's Algorithm and TCP_NODELAY

**Nagle's algorithm** buffers small writes and sends them together to reduce the number of small packets. It holds a partial segment until either: (a) the previous segment is acknowledged, or (b) enough data accumulates to fill a segment.

```python
# Problem: Nagle + delayed ACK can cause 40ms+ latency
socket.send(b"tag1=val1|")   # Small write, Nagle buffers it
socket.send(b"tag2=val2|")   # Still buffered, waiting for ACK
# ... 40ms delay before the buffered data is sent
```

**For trading, ALWAYS disable Nagle:**
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
```

`TCP_NODELAY` disables Nagle's algorithm, sending every write immediately regardless of size. The small-packet overhead is negligible compared to the latency reduction in trading.

#### SO_REUSEADDR

```python
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

Allows binding to an address that's in `TIME_WAIT` state (after a recent close). Without this, restarting a trading application may fail with "Address already in use" for up to 2 minutes. Essential for any production trading system that may need rapid restarts.

#### SO_KEEPALIVE

Sends periodic probe packets on idle connections to detect dead peers. Configurable parameters:
- `TCP_KEEPIDLE`: Time before first probe (default 7200s — way too long for trading)
- `TCP_KEEPINTVL`: Interval between probes
- `TCP_KEEPCNT`: Number of failed probes before connection is considered dead

```python
sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)    # 10 seconds
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)    # 5 seconds
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)      # 3 failures
```

**Trading context:** Detecting a dead FIX session quickly is critical. If the exchange goes down and you don't know, you'll queue orders that never arrive.

### 3. UDP and Why HFT Uses It

UDP provides unreliable, unordered datagram delivery. No handshake, no retransmission, no flow control, no congestion control.

**Why UDP for market data:**
1. **Multicast support**: One sender, many receivers. The exchange sends once, and all subscribers receive simultaneously. TCP is point-to-point only.
2. **No head-of-line blocking**: TCP delivers data in order — if packet 5 is lost, packets 6, 7, 8 are held until packet 5 is retransmitted. With UDP, you get 6, 7, 8 immediately and can detect the gap via sequence numbers.
3. **Lower latency**: No handshake, no Nagle, no delayed ACK, no congestion window ramp-up.
4. **Natural fit for market data**: A missed tick is stale anyway. Retransmitting a 1-second-old price is worse than processing the current price with a gap.

**The trade-off:** UDP doesn't guarantee delivery. Market data feeds include sequence numbers so receivers can detect gaps and request retransmissions via a separate recovery mechanism.

### 4. Multicast

Multicast sends one packet to a group of interested receivers. The network infrastructure (routers, switches) replicates the packet only where subscribers exist.

**Multicast addressing:** 224.0.0.0 - 239.255.255.255 (Class D addresses). Exchange market data feeds use assigned multicast groups.

**IGMP (Internet Group Management Protocol):** Hosts use IGMP to tell routers they want to join or leave a multicast group. Routers use IGMP queries to determine which groups have active members.

```python
import socket
import struct

# Join a multicast group for CME market data
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 30001))  # Bind to the multicast port

# Join the multicast group
mreq = struct.pack('4s4s',
    socket.inet_aton('224.0.31.1'),    # Multicast group
    socket.inet_aton('10.1.1.100'))    # Local interface
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive market data
while True:
    data, addr = sock.recvfrom(65535)
    process_market_data(data)
```

**Exchange feed architecture:**
```
Exchange Data Center
   |
   | Multicast (224.0.31.x)
   |
   +--- Switch ---- Trading Firm A (subscribed to ESM5, NQM5)
   |
   +--- Switch ---- Trading Firm B (subscribed to ESM5 only)
   |
   +--- Switch ---- Trading Firm C (subscribed to NQM5, ZNM5)
```

Each firm joins only the multicast groups for instruments they trade. The exchange sends to the group address, and the network delivers to all members.

### 5. FIX Protocol

FIX (Financial Information eXchange) is the dominant protocol for electronic trading. It's a text-based, tag-value protocol.

#### Message Structure

```
8=FIX.4.4|9=148|35=D|49=SENDER|56=TARGET|34=12|52=20240411-10:30:00|
11=ORDER001|55=ESM5|54=1|38=100|40=2|44=5250.25|10=185|
```

Each field is `tag=value` separated by SOH (ASCII 1, shown as `|`):
- **Tag 8** (BeginString): Protocol version
- **Tag 9** (BodyLength): Length of message body
- **Tag 35** (MsgType): Message type (D = New Order Single, 8 = Execution Report)
- **Tag 49** (SenderCompID): Sender identification
- **Tag 56** (TargetCompID): Target identification
- **Tag 34** (MsgSeqNum): Message sequence number
- **Tag 10** (CheckSum): 3-digit modulo-256 checksum

Common MsgTypes:
| Tag 35 | Meaning |
|---|---|
| A | Logon |
| 0 | Heartbeat |
| 1 | Test Request |
| 2 | Resend Request |
| 4 | Sequence Reset |
| 5 | Logout |
| D | New Order - Single |
| F | Order Cancel Request |
| G | Order Cancel/Replace |
| 8 | Execution Report |

#### Session Layer vs Application Layer

**Session layer** handles connectivity:
- Logon/Logout (message types A, 5)
- Heartbeats (type 0) — sent at regular intervals to confirm connectivity
- Test Requests (type 1) — sent when heartbeat is missed
- Sequence number management
- Message recovery (Resend Request type 2, Sequence Reset type 4)

**Application layer** handles business logic:
- New orders (type D)
- Cancel/Replace (types F, G)
- Execution reports (type 8)
- Market data (types W, X)

#### Sequence Numbers

Every FIX message has a monotonically increasing sequence number (Tag 34). Both sides track:
- **Next expected incoming sequence number**
- **Next outgoing sequence number**

If a message arrives with a sequence number higher than expected, the receiver sends a Resend Request for the missing messages. If lower than expected (possible duplicate), it's checked for PossDupFlag (Tag 43).

**Why this matters:** Sequence gaps mean missed messages. A missed Execution Report means you don't know if your order was filled. A missed cancel acknowledgment means you might think an order is still active when it's been cancelled.

#### Recovery Flow
```
Client                          Exchange
  |--- Logon (seq=1) ------------>|
  |<-- Logon (seq=1) -------------|
  |--- New Order (seq=2) -------->|
  |<-- Exec Report (seq=2) -------|  (order acknowledged)
  |                                |
  | [NETWORK BLIP - seq 3 lost]   |
  |                                |
  |<-- Exec Report (seq=4) -------|  (seq gap detected!)
  |--- Resend Request (3-3) ----->|  (request missing messages)
  |<-- Seq Reset or Resend -------|
  | [Gap filled, continue]         |
```

### 6. Socket Programming

#### select, poll, epoll

These are I/O multiplexing mechanisms that let a single thread monitor multiple file descriptors (sockets) for readiness.

**select():**
- Monitors up to `FD_SETSIZE` (typically 1024) file descriptors
- Returns which FDs are ready for read/write/exception
- O(n) per call — kernel scans all monitored FDs
- Portable but slow for many connections

**poll():**
- No FD limit
- Same O(n) scanning as select
- Slightly cleaner API (no fd_set manipulation)

**epoll() (Linux-specific):**
- O(1) for returning ready FDs (kernel maintains a ready list)
- Scales to hundreds of thousands of connections
- Two modes:
  - **Level-triggered (LT)**: Reports readiness as long as the FD is ready (like select/poll)
  - **Edge-triggered (ET)**: Reports readiness only when state changes (more efficient but requires non-blocking I/O and draining the buffer completely)

```python
import select

# epoll example
epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN)

while True:
    events = epoll.poll(timeout=1.0)
    for fd, event in events:
        if fd == server_socket.fileno():
            conn, addr = server_socket.accept()
            epoll.register(conn.fileno(), select.EPOLLIN)
        elif event & select.EPOLLIN:
            data = connections[fd].recv(4096)
            process(data)
```

**Trading context:** A FIX gateway managing connections to multiple exchanges uses epoll to monitor all connections in a single thread. When any connection has data, the thread wakes and processes it immediately.

#### Non-Blocking I/O

By default, socket operations block until they complete. Non-blocking mode returns immediately with an error (`EAGAIN`/`EWOULDBLOCK`) if the operation can't complete.

```python
sock.setblocking(False)

try:
    data = sock.recv(4096)
except BlockingIOError:
    pass  # No data available yet
```

Combined with epoll, non-blocking I/O lets a single thread handle thousands of connections efficiently.

### 7. Latency Concepts

#### Network Hops and Serialization Delay

**Propagation delay:** Speed-of-light delay. ~5 microseconds per kilometer in fiber. Co-location puts you within meters of the exchange matching engine.

**Serialization delay:** Time to push bits onto the wire. For a 100-byte packet on 10 Gbps Ethernet: 100 * 8 / 10^10 = 80 nanoseconds. Negligible at modern speeds.

**Switch latency:** Each network switch adds ~1-5 microseconds (cut-through switches) or more (store-and-forward). Minimizing hops matters.

**Kernel processing:** The OS network stack (interrupt handling, protocol processing, buffer copies) adds ~10-50 microseconds. This is often the dominant latency in a co-located setup.

#### Kernel Bypass: DPDK and OpenOnload

The Linux kernel network stack is designed for generality, not minimal latency. Kernel bypass techniques move packet processing to userspace:

**DPDK (Data Plane Development Kit):**
- Polls the NIC directly from userspace (no interrupts)
- Uses huge pages for buffer memory
- Processes packets in userspace without kernel involvement
- Latency: ~1-5 microseconds (vs. ~10-50 with kernel)
- Drawback: Dedicates CPU cores to polling, no standard socket API

**OpenOnload (Solarflare/Xilinx):**
- Kernel bypass library that intercepts standard socket calls
- Applications use normal socket API but packets bypass the kernel
- Easier to adopt than DPDK (no code changes)
- Latency: ~2-10 microseconds

**Zero-copy:**
Standard networking copies data multiple times:
1. NIC DMA to kernel buffer
2. Kernel buffer to userspace buffer (via `recv()`)

Zero-copy techniques eliminate copies:
- `sendfile()`: Send file data directly from kernel page cache to NIC
- `MSG_ZEROCOPY`: Let the kernel send directly from userspace buffer
- DPDK: Userspace accesses NIC buffers directly

```
Traditional:   NIC -> Kernel buffer -> User buffer -> Application
                           (copy 1)        (copy 2)

Zero-copy:     NIC -> Shared buffer (mapped to userspace) -> Application
                           (no copies)
```

#### Co-location Architecture
```
Exchange Data Center
+-----------------------------------------------+
|                                                 |
|  Exchange      Cross-connect   Trading Firm    |
|  Matching  <---  (fiber)  ---> Co-lo Cabinet   |
|  Engine         < 1 meter       |              |
|                                 +-- Server     |
|                                 +-- FPGA NIC   |
|                                 +-- Switch     |
+-----------------------------------------------+

Round-trip latency budget (order send to ack):
  Application processing:   1-5 us
  Kernel bypass network:    1-3 us
  Wire propagation:         < 1 us
  Exchange matching:        1-10 us
  --------------------------------
  Total:                    ~5-20 us
```

---

## Practice Questions (20-30 min)

1. **Walk through the TCP three-way handshake. Why does it require three packets instead of two?**

2. **Explain Nagle's algorithm. Why is it harmful for trading systems? What socket option disables it, and what is the trade-off?**

3. **Your FIX session receives a message with sequence number 47, but you expected 45. Describe the recovery process step by step.**

4. **Compare TCP and UDP for market data delivery. Why do exchanges typically use UDP multicast for market data but TCP for order entry?**

5. **Explain the difference between select, poll, and epoll. Why is epoll preferred for a trading gateway that connects to 50 exchanges?**

6. **What is kernel bypass? Compare DPDK and OpenOnload in terms of latency, ease of adoption, and trade-offs.**

7. **Describe the multicast join process. What happens at the IGMP level when your application calls `IP_ADD_MEMBERSHIP`?**

8. **Your trading system experiences occasional 40ms latency spikes on order sends. The network is fine. What TCP-level issues could cause this? How would you diagnose?**

9. **Explain SO_REUSEADDR and TIME_WAIT. Why is SO_REUSEADDR essential for a trading application?**

10. **Design a market data handler that receives multicast UDP data from 3 exchanges, detects gaps using sequence numbers, and requests retransmissions. What data structures and patterns would you use?**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** The TCP three-way handshake involves which sequence of packets?
- (A) SYN, ACK, SYN-ACK
- (B) SYN, SYN-ACK, ACK
- (C) ACK, SYN, SYN-ACK
- (D) SYN, SYN, ACK

**Q2.** TCP_NODELAY disables which algorithm?
- (A) Slow Start
- (B) Nagle's algorithm
- (C) Congestion Avoidance
- (D) Delayed ACK

**Q3.** Which I/O multiplexing mechanism scales to hundreds of thousands of connections with O(1) event retrieval?
- (A) select
- (B) poll
- (C) epoll
- (D) kqueue

**Q4.** In FIX protocol, Tag 35=D represents:
- (A) Execution Report
- (B) Heartbeat
- (C) New Order - Single
- (D) Logon

**Q5.** Why do exchanges use UDP multicast for market data instead of TCP?
- (A) UDP is more reliable than TCP
- (B) UDP supports one-to-many delivery without per-subscriber connections
- (C) UDP provides ordered delivery
- (D) UDP has built-in compression

**Q6.** What is the typical latency added by the Linux kernel network stack for a co-located trading system?
- (A) < 1 nanosecond
- (B) 10-50 microseconds
- (C) 1-5 milliseconds
- (D) 10-100 milliseconds

**Q7.** TCP head-of-line blocking occurs when:
- (A) The sender's buffer is full
- (B) A lost packet prevents delivery of subsequent in-order packets
- (C) The receiver's window is zero
- (D) The connection is reset

**Q8.** SO_KEEPALIVE is used to:
- (A) Keep the socket open after the process exits
- (B) Detect dead peer connections by sending periodic probes
- (C) Prevent the kernel from closing idle sockets
- (D) Keep the TCP window open

**Q9.** In FIX, when you receive a message with a sequence number higher than expected, you should:
- (A) Ignore it
- (B) Reset your sequence numbers
- (C) Send a Resend Request for the missing messages
- (D) Disconnect and reconnect

**Q10.** DPDK achieves low latency primarily by:
- (A) Using faster network cables
- (B) Bypassing the kernel network stack and processing packets in userspace
- (C) Compressing all network traffic
- (D) Using multiple TCP connections

### Short Answer

**Q11.** Explain the difference between TCP flow control (receive window) and congestion control (congestion window). Which one limits the sender's transmission rate?

**Q12.** A FIX message checksum (Tag 10) is computed how? Why is it insufficient for data integrity?

**Q13.** Describe edge-triggered vs. level-triggered epoll. When would you use each in a trading system?

**Q14.** What is the TIME_WAIT state in TCP? How long does it last, and why does it exist? Why is SO_REUSEADDR needed?

**Q15.** Your market data handler receives UDP packets with sequence numbers [100, 101, 103, 104, 102]. Describe how you would handle this to ensure ordered processing.

**Q16.** Explain zero-copy networking. Describe the data path for a received packet with and without zero-copy.

**Q17.** What is the difference between co-location and proximity hosting? Which does Jump Trading use and why?

---

## Quiz Answer Key

**Q1: (B)** SYN, SYN-ACK, ACK. The client initiates with SYN, the server responds with SYN-ACK (acknowledging the client's SYN and sending its own), and the client completes with ACK.

**Q2: (B)** Nagle's algorithm. Nagle buffers small writes to reduce packet overhead. TCP_NODELAY disables this, ensuring each write is sent immediately — essential for low-latency trading.

**Q3: (C)** epoll. It maintains a ready list in the kernel, so `epoll_wait()` returns only the ready file descriptors in O(1). select and poll scan all monitored FDs each time (O(n)). kqueue is the BSD equivalent of epoll.

**Q4: (C)** New Order - Single. Tag 35 is MsgType. D = New Order Single, 8 = Execution Report, A = Logon, 0 = Heartbeat.

**Q5: (B)** UDP multicast sends one packet that's replicated by the network to all subscribers. TCP would require separate connections and separate sends to each subscriber, which doesn't scale when thousands of firms need the same data.

**Q6: (B)** 10-50 microseconds. This includes interrupt handling, protocol processing, and buffer copies. Kernel bypass (DPDK, OpenOnload) reduces this to 1-5 microseconds.

**Q7: (B)** If packet N is lost, TCP holds packets N+1, N+2, N+3 in the receive buffer until N is retransmitted and received. The application doesn't see any of them until the gap is filled. This is why UDP is preferred for market data — you'd rather process N+1 immediately and handle the gap separately.

**Q8: (B)** SO_KEEPALIVE sends TCP keepalive probes on idle connections. If the peer doesn't respond after the configured number of probes, the connection is marked as dead. This detects scenarios like a remote server crash, network partition, or unplugged cable.

**Q9: (C)** Send a Resend Request (MsgType 2) specifying the range of missing sequence numbers. The sender will retransmit the missing messages (possibly with PossDupFlag set) or send a Sequence Reset if the messages are no longer available.

**Q10: (B)** DPDK maps NIC memory directly to userspace and uses polling instead of interrupts. Packets go directly from the NIC to the application without traversing the kernel network stack, eliminating interrupt overhead, context switches, and buffer copies.

**Q11:** Flow control (rwnd) prevents the sender from overwhelming the receiver's buffer. Congestion control (cwnd) prevents the sender from overwhelming the network. The effective sending window is `min(rwnd, cwnd)` — whichever is smaller limits the rate. They serve different purposes: flow control is end-to-end between sender and receiver; congestion control is about the network path between them.

**Q12:** The FIX checksum (Tag 10) is the sum of all bytes in the message (from Tag 8 to the SOH before Tag 10), modulo 256, expressed as a 3-digit string. It's insufficient because: (a) modulo 256 has high collision probability, (b) it can't detect byte reordering, (c) it's not cryptographic. It's meant to catch transmission corruption, not adversarial modification. For integrity, TLS is used on the transport layer.

**Q13:** Level-triggered (LT) reports readiness as long as the socket has data available — even if you've already been notified. Edge-triggered (ET) only reports when the state changes (e.g., new data arrives). ET is more efficient (fewer wakeups) but requires non-blocking I/O and reading until EAGAIN to drain the buffer completely. In trading, ET is preferred for the hot path to minimize unnecessary wakeups, but LT is simpler and safer for less latency-critical components.

**Q14:** TIME_WAIT is a TCP state entered by the side that initiates connection close. It lasts for 2 * MSL (Maximum Segment Lifetime, typically 60 seconds = 2 minutes total). It exists to: (a) ensure the final ACK reaches the peer (if lost, the peer will retransmit FIN), and (b) prevent old packets from a previous connection being misinterpreted as part of a new connection on the same port. SO_REUSEADDR allows binding to a port in TIME_WAIT, essential for trading systems that need quick restarts.

**Q15:** Use a resequencing buffer. Maintain the next expected sequence number (101 after receiving 100). When 101 arrives, process it and advance to 102. When 103 arrives, buffer it (gap detected — 102 is missing). When 104 arrives, buffer it. When 102 arrives, process 102, then check the buffer for 103 (found, process), then 104 (found, process). Set a timeout for missing packets — if 102 doesn't arrive within X microseconds, either request retransmission or skip and log the gap.

**Q16:** Traditional path: NIC DMA writes to kernel ring buffer -> kernel copies to socket receive buffer -> `recv()` copies to userspace application buffer. Two copies, two context switches. Zero-copy path: NIC DMA writes to a buffer that is memory-mapped into both kernel and userspace. The application reads directly from the DMA buffer with no copies. DPDK goes further by having userspace manage the NIC directly, eliminating all kernel involvement.

**Q17:** Co-location places your servers in the same data center as the exchange's matching engine, typically within the same building, connected via cross-connects (direct fiber runs). Proximity hosting places servers near (but not in) the exchange data center. Co-location provides the lowest possible latency (often < 1 microsecond wire delay). Jump Trading uses co-location at major exchanges (CME, ICE, ASX, etc.) because in competitive market-making, even microseconds of advantage translate to meaningful edge. The cost is significant (rack space, cross-connect fees, dedicated infrastructure), but the latency advantage justifies it for a firm operating at Jump's scale.
