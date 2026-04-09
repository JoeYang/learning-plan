# Day 5 (Mon Apr 13) — Linux Systems & OS Fundamentals

## Overview (5 min)

Jump Trading's infrastructure runs on Linux. Every component — from market data handlers to order routers to risk engines — is a Linux process, and the firm's edge depends on squeezing maximum performance from the OS. A Futures Execution Services engineer must understand process management, memory architecture, file I/O, scheduling, and performance tuning at a level that goes far beyond casual familiarity. Interviewers will probe your ability to reason about system-level behavior: "Why is this process slow? How would you reduce latency? What happens when..."

---

## Reading Materials (60-90 min)

### 1. Processes and Threads

#### Process Creation: fork() and exec()

`fork()` creates a new process by duplicating the calling process. The child gets a copy of the parent's memory space (using copy-on-write — pages are shared until either process writes to them).

```c
pid_t pid = fork();
if (pid == 0) {
    // Child process
    execvp("./trading_engine", args);  // Replace child's image
} else if (pid > 0) {
    // Parent process
    waitpid(pid, &status, 0);  // Wait for child
} else {
    // fork failed
}
```

`exec()` family replaces the current process image with a new program. After `exec`, the calling process's code, data, and stack are replaced — it never returns (unless it fails).

**Why fork+exec matters for trading:** Process isolation. A crash in the market data handler doesn't bring down the order router if they're separate processes. Many trading systems use a "supervisor" process that forks child processes and restarts them on failure.

#### Process States

```
          fork()
            |
            v
   +--- CREATED ---+
   |               |
   v               |
READY  <------  RUNNING
   |      ^         |
   |      |         | I/O request,
   |   scheduled    | sleep, wait
   |      |         |
   |      |         v
   |      +---- BLOCKED/WAITING
   |
   +---> ZOMBIE (exited but parent hasn't called wait())
   |
   +---> TERMINATED
```

**Zombie processes:** When a child exits, it becomes a zombie — its exit status is retained in the process table until the parent calls `wait()`. If the parent never calls `wait()`, zombies accumulate. In a long-running trading system, this is a resource leak.

```bash
# Detect zombies
ps aux | grep Z
```

**Orphan processes:** If a parent exits before its children, the children are adopted by `init` (PID 1), which automatically reaps them.

#### Context Switching

A context switch saves the current process's registers, program counter, and stack pointer, then loads another process's state. Cost: typically 1-10 microseconds, but the real cost is cache pollution — after a switch, the CPU cache contains the old process's data, causing cold cache misses.

**Trading impact:** Frequent context switches between the market data thread and the order execution thread can cause latency spikes. CPU pinning (discussed below) eliminates involuntary switches.

### 2. Memory

#### Virtual Memory and Page Tables

Every process has its own virtual address space (typically 48-bit on x86-64 = 256 TB). The MMU (Memory Management Unit) translates virtual addresses to physical addresses using **page tables**.

```
Virtual Address Space (per process)        Physical Memory
+------------------+                      +------------------+
| Stack            | ---+                 | Frame 0          |
+------------------+    |   Page Table    +------------------+
| ...              |    +-->| VPN -> PFN  | Frame 1          |
+------------------+        | 0x400 -> 7  | +------------------+
| Heap             | ------>| 0x600 -> 3  | Frame 2          |
+------------------+        | ...         | +------------------+
| Data             |        +-------------+ ...              |
+------------------+                      +------------------+
| Text (code)      |
+------------------+
```

Pages are typically 4 KB. A 48-bit address space with 4 KB pages means 2^36 page table entries — too many for a flat table. Linux uses a **multi-level page table** (4 levels on x86-64: PGD -> PUD -> PMD -> PTE) so only populated regions consume memory.

#### TLB (Translation Lookaside Buffer)

The TLB is a hardware cache of recent virtual-to-physical translations. A TLB hit resolves in ~1 cycle. A TLB miss requires walking the page table (10-100 cycles with hardware page walker).

**Problem for trading:** With a 4 KB page size, 64 TLB entries cover only 256 KB of memory. A trading application with large data structures (order books, position maps) will have frequent TLB misses.

#### Huge Pages

Instead of 4 KB pages, use 2 MB or 1 GB pages. This drastically reduces TLB misses:
- 64 TLB entries * 4 KB = 256 KB coverage
- 64 TLB entries * 2 MB = 128 MB coverage
- 64 TLB entries * 1 GB = 64 GB coverage

```bash
# Allocate huge pages at boot
echo 1024 > /proc/sys/vm/nr_hugepages  # 1024 x 2MB = 2GB

# Or use transparent huge pages (THP)
echo always > /sys/kernel/mm/transparent_hugepage/enabled
```

**Trading application:**
```c
// mmap with huge pages
void *ptr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
```

**Caveat:** THP can cause latency spikes when the kernel merges or splits huge pages. Many HFT firms disable THP and use explicit huge page allocation.

#### mmap and Shared Memory

`mmap()` maps a file or anonymous memory region into the process's address space.

```c
// Map a file into memory
int fd = open("market_data.bin", O_RDONLY);
void *data = mmap(NULL, file_size, PROT_READ, MAP_PRIVATE, fd, 0);
// Access data directly without read() calls
price = ((struct Tick *)data)[i].price;
```

**Shared memory** (`shm_open` + `mmap` with `MAP_SHARED`) allows multiple processes to access the same physical memory. This is the fastest IPC mechanism — no copies, no kernel transitions for data access.

```c
// Process A: Create and write
int fd = shm_open("/order_book", O_CREAT | O_RDWR, 0666);
ftruncate(fd, sizeof(OrderBook));
OrderBook *book = mmap(NULL, sizeof(OrderBook), PROT_READ | PROT_WRITE,
                       MAP_SHARED, fd, 0);
book->best_bid = 5250.25;

// Process B: Open and read
int fd = shm_open("/order_book", O_RDONLY, 0);
OrderBook *book = mmap(NULL, sizeof(OrderBook), PROT_READ,
                       MAP_SHARED, fd, 0);
printf("Best bid: %f\n", book->best_bid);
```

**Trading use case:** Shared memory between the market data handler and the strategy engine. The handler writes updates, the strategy reads them — zero-copy, lowest possible latency.

### 3. File I/O

#### File Descriptors

Every open file, socket, and pipe is represented by a non-negative integer (file descriptor). Standard: 0 = stdin, 1 = stdout, 2 = stderr. The kernel maintains a per-process file descriptor table pointing to kernel file objects.

```bash
# See open FDs for a process
ls -la /proc/<pid>/fd
```

#### Buffered vs Unbuffered I/O

**Buffered I/O** (stdio: `fread`, `fwrite`, `fprintf`): The C library maintains a userspace buffer and batches writes to reduce system calls. Default: line-buffered for terminals, fully buffered for files (typically 4-8 KB).

**Unbuffered I/O** (POSIX: `read`, `write`): Each call is a system call that goes directly to the kernel. More control but more overhead per small write.

```c
// Buffered — library batches writes
FILE *f = fopen("log.txt", "w");
fprintf(f, "order %d filled\n", id);  // May not write immediately
fflush(f);  // Force flush to kernel

// Unbuffered — direct system call
int fd = open("log.txt", O_WRONLY | O_CREAT, 0644);
write(fd, buf, len);  // Immediate system call
```

#### O_DIRECT and Page Cache

The Linux **page cache** caches recently read/written file data in memory. This helps most applications but hurts when:
- You're doing sequential reads of large files (cache is wasted — data is read once)
- You want predictable latency (cache eviction can cause spikes)

`O_DIRECT` bypasses the page cache, going straight to disk:
```c
int fd = open("data.bin", O_RDONLY | O_DIRECT);
// Reads go directly to/from disk — no page cache
// Buffer must be aligned (typically to 512 bytes or page size)
```

**Trading context:** Market data recording (writing tick data to disk) may use `O_DIRECT` to avoid polluting the page cache with write data, which could evict frequently-accessed read data from the cache.

### 4. Signals

Signals are asynchronous notifications sent to a process. Common signals:

| Signal | Default Action | Common Use |
|---|---|---|
| SIGTERM (15) | Terminate | Graceful shutdown request |
| SIGKILL (9) | Terminate | Force kill (cannot be caught) |
| SIGINT (2) | Terminate | Ctrl+C |
| SIGHUP (1) | Terminate | Terminal hangup / config reload |
| SIGUSR1 (10) | Terminate | User-defined |
| SIGCHLD (17) | Ignore | Child process state change |
| SIGPIPE (13) | Terminate | Write to broken pipe |
| SIGSEGV (11) | Core dump | Segmentation fault |

```python
import signal
import sys

def graceful_shutdown(signum, frame):
    """Cancel all open orders before exiting."""
    cancel_all_orders()
    close_fix_sessions()
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

**Trading critical:** SIGPIPE — if the exchange closes the connection and you write to the socket, your process gets SIGPIPE and terminates by default. Always handle or ignore SIGPIPE in trading systems:
```python
signal.signal(signal.SIGPIPE, signal.SIG_IGN)
```

### 5. Scheduling

#### CFS (Completely Fair Scheduler)

Linux's default scheduler. Uses a red-black tree of runnable tasks, keyed by "virtual runtime" (vruntime). The task with the smallest vruntime runs next. This ensures proportional CPU time based on priority.

**Nice values** (-20 to +19): Lower nice = higher priority = more CPU time. A task with nice -20 gets ~100x more CPU time than one with nice +19.

```bash
nice -n -10 ./strategy_engine    # Higher priority
renice -n -5 -p <pid>            # Change running process
```

#### Real-Time Scheduling

For latency-critical tasks, Linux offers real-time scheduling policies:

**SCHED_FIFO:** Real-time FIFO. The task runs until it blocks or yields. Higher-priority RT tasks preempt lower-priority ones. No time slicing.

**SCHED_RR:** Real-time round-robin. Like SCHED_FIFO but with time slicing among tasks of the same priority.

```bash
chrt -f 50 ./market_data_handler   # SCHED_FIFO, priority 50
chrt -r 30 ./order_router          # SCHED_RR, priority 30
```

Real-time priorities (1-99) always preempt CFS tasks. Priority 99 is highest.

**Warning:** A SCHED_FIFO task that never blocks will starve all lower-priority tasks, including the OS. Use with extreme care.

#### CPU Pinning

Bind a process/thread to specific CPU cores to eliminate migration between cores (which causes cache misses).

```bash
# Pin process to cores 2 and 3
taskset -c 2,3 ./trading_engine

# Pin a running process
taskset -c 4 -p <pid>
```

**`isolcpus`** kernel parameter: Reserves CPUs from the general scheduler. No other process will be scheduled on these CPUs.

```bash
# In kernel command line (grub)
isolcpus=2,3,4,5

# Now only explicitly pinned tasks run on cores 2-5
taskset -c 2 ./market_data_handler
taskset -c 3 ./order_router
```

### 6. IPC (Inter-Process Communication)

| Mechanism | Speed | Complexity | Use Case |
|---|---|---|---|
| Pipe | Medium | Low | Parent-child data flow |
| Named pipe (FIFO) | Medium | Low | Unrelated processes, simple stream |
| Shared memory | Fastest | High | High-throughput data sharing |
| Message queue | Medium | Medium | Structured message passing |
| Unix domain socket | Fast | Medium | Local client-server, like TCP but faster |
| Signal | N/A | Low | Simple notifications |

**Shared memory** is the gold standard for trading IPC — zero-copy, no kernel involvement for data access. But it requires careful synchronization (atomics, memory barriers, or lock-free structures).

**Unix domain sockets** are like TCP sockets but for same-machine communication. They skip the entire network stack (no checksumming, no routing), making them ~2-3x faster than TCP loopback.

```python
import socket

# Server
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind("/tmp/trading.sock")
server.listen(5)

# Client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect("/tmp/trading.sock")
```

### 7. Performance Tools

#### Process and System Monitoring

```bash
# Real-time process monitor
top -H -p <pid>      # -H shows threads
htop                  # Interactive, per-core view

# System-wide statistics
vmstat 1              # Virtual memory stats every 1 second
iostat -x 1           # Disk I/O stats
sar -n DEV 1          # Network stats
```

#### Tracing and Profiling

```bash
# System call tracing
strace -c ./trading_engine          # Summary of syscalls
strace -e trace=network -p <pid>    # Trace network syscalls only
strace -T -e write -p <pid>         # Show time spent in each write()

# Library call tracing
ltrace -c ./trading_engine          # Summary of library calls

# CPU profiling
perf record -g ./trading_engine     # Record with call graphs
perf report                         # Interactive analysis
perf stat ./trading_engine          # CPU counters (cache misses, IPC)
```

#### Network Diagnostics

```bash
# Socket statistics (replacement for netstat)
ss -tlnp              # TCP listening sockets with process info
ss -i                 # TCP socket internal info (cwnd, rwnd, RTT)
ss -s                 # Summary statistics

# Packet capture
tcpdump -i eth0 port 9823 -w capture.pcap    # Capture FIX traffic
tcpdump -i eth0 -nn 'udp and dst 224.0.31.1' # Capture multicast
```

### 8. Kernel Tuning for Low Latency

#### isolcpus and IRQ Affinity

```bash
# Isolate CPUs 2-7 from the scheduler
# /etc/default/grub: GRUB_CMDLINE_LINUX="isolcpus=2-7"

# Assign network interrupts to specific CPUs
echo 2 > /proc/irq/48/smp_affinity_list  # NIC IRQs on CPU 2
```

This ensures that network interrupts are handled on a dedicated CPU, and the trading application's CPUs are never interrupted.

#### Disabling Hyper-Threading

Hyper-threading shares CPU resources (caches, execution units) between two logical cores. For latency-sensitive work, this sharing causes unpredictable contention:

```bash
# Disable HT at runtime
echo 0 > /sys/devices/system/cpu/cpu1/online  # Disable sibling core
# Or in BIOS
```

#### NUMA (Non-Uniform Memory Access)

Multi-socket systems have memory attached to each CPU socket. Accessing local memory is faster (~100ns) than remote memory (~200ns).

```
  Socket 0             Socket 1
  +--------+           +--------+
  | CPU 0-3|           | CPU 4-7|
  +--------+           +--------+
      |                     |
  +--------+           +--------+
  | Memory |           | Memory |
  | (local)|           | (local)|
  +--------+           +--------+
```

```bash
# Pin process to NUMA node 0 (CPUs and memory)
numactl --cpunodebind=0 --membind=0 ./trading_engine

# Check NUMA topology
numactl --hardware
```

**Complete low-latency setup:**
```bash
# 1. Isolate CPUs
# GRUB: isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7

# 2. Pin trading process to isolated core
taskset -c 3 chrt -f 90 ./trading_engine

# 3. Pin NIC IRQs to a separate isolated core
echo 2 > /proc/irq/<nic_irq>/smp_affinity_list

# 4. Use huge pages
echo 512 > /proc/sys/vm/nr_hugepages

# 5. Disable power management
echo performance > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor

# 6. Set real-time scheduling
# (done via chrt above)
```

---

## Practice Questions (20-30 min)

1. **Explain the fork/exec model. Why does Unix separate process creation (fork) from program loading (exec)? What is copy-on-write?**

2. **What is a zombie process? How do they occur and how do you prevent them in a long-running trading system?**

3. **Explain virtual memory and page tables. Why does Linux use multi-level page tables?**

4. **Your trading application has high TLB miss rates. What causes this, and what techniques would you use to reduce TLB misses?**

5. **Compare shared memory and Unix domain sockets for IPC in a trading system. When would you use each?**

6. **Describe the Linux process scheduling landscape. How would you configure scheduling for a latency-critical market data handler?**

7. **You're debugging a trading application that's occasionally slow. Walk through the performance tools you'd use, in order, and what each tells you.**

8. **Explain NUMA. Why does NUMA-aware memory allocation matter for a trading system? What happens if you get it wrong?**

9. **What is `O_DIRECT` and when would you use it? What are the constraints and trade-offs?**

10. **Design a low-latency Linux configuration for a trading server. Cover CPU isolation, scheduling, memory, interrupts, and power management.**

---

## Quiz (15-20 questions)

### Multiple Choice

**Q1.** `fork()` creates a new process by:
- (A) Loading a new program from disk
- (B) Duplicating the calling process with copy-on-write semantics
- (C) Creating a new thread in the same process
- (D) Allocating an empty process and starting it from main()

**Q2.** A zombie process is:
- (A) A process that consumes excessive CPU
- (B) A process that has exited but whose parent hasn't called wait()
- (C) A process stuck in an infinite loop
- (D) A process that has lost its parent

**Q3.** The TLB is:
- (A) A cache of file system metadata
- (B) A hardware cache of virtual-to-physical address translations
- (C) A software cache maintained by the kernel
- (D) A buffer for network packets

**Q4.** Huge pages reduce latency primarily by:
- (A) Reducing disk I/O
- (B) Reducing TLB misses
- (C) Increasing network throughput
- (D) Enabling faster context switches

**Q5.** Which IPC mechanism provides the lowest latency for data sharing?
- (A) TCP loopback
- (B) Pipes
- (C) Shared memory
- (D) Message queues

**Q6.** `isolcpus` kernel parameter:
- (A) Increases the speed of isolated CPUs
- (B) Prevents the scheduler from placing general tasks on specified CPUs
- (C) Disables the specified CPUs entirely
- (D) Enables hyper-threading on specified CPUs

**Q7.** Which scheduling policy provides the most deterministic latency?
- (A) CFS with nice -20
- (B) SCHED_FIFO
- (C) SCHED_BATCH
- (D) SCHED_IDLE

**Q8.** `strace` shows:
- (A) Library function calls
- (B) System calls made by a process
- (C) CPU performance counters
- (D) Network packet contents

**Q9.** `O_DIRECT` flag causes file I/O to:
- (A) Use asynchronous I/O
- (B) Bypass the page cache
- (C) Use memory-mapped I/O
- (D) Compress data before writing

**Q10.** In NUMA architecture, accessing remote memory is:
- (A) The same speed as local memory
- (B) Faster than local memory due to caching
- (C) Slower than local memory (~2x latency)
- (D) Impossible without special system calls

### Short Answer

**Q11.** Explain the difference between `perf stat` and `perf record`. When would you use each?

**Q12.** What is the page cache? How does it help most applications? When does it hurt?

**Q13.** A process calls `write()` to a socket. Trace the path from userspace to the network, listing each copy of the data.

**Q14.** Explain IRQ affinity. Why would you set NIC interrupts to a specific CPU in a trading system?

**Q15.** What does `nohz_full` kernel parameter do? Why is it useful for latency-sensitive applications?

**Q16.** Compare `SIGTERM` and `SIGKILL`. Why should a trading application handle SIGTERM gracefully?

**Q17.** You see high `context switches/sec` in `vmstat`. What could cause this, and how would it affect a trading application?

**Q18.** Explain copy-on-write (COW) in the context of `fork()`. What triggers the actual copy?

---

## Quiz Answer Key

**Q1: (B)** `fork()` duplicates the calling process. The child gets copies of the parent's memory space, file descriptors, and signal handlers. Physical memory pages are shared and marked copy-on-write — actual copying occurs only when either process writes to a page.

**Q2: (B)** A zombie is a process that has terminated but still has an entry in the process table because the parent hasn't read its exit status via `wait()`/`waitpid()`. Zombies consume no CPU or memory (except the process table entry) but can exhaust the process table if they accumulate.

**Q3: (B)** The TLB (Translation Lookaside Buffer) is a hardware cache on the CPU that stores recent virtual page number to physical frame number mappings. A TLB hit resolves address translation in ~1 cycle. A miss requires a page table walk (10-100 cycles).

**Q4: (B)** A 2 MB huge page covers 512x more memory than a 4 KB page, so the same number of TLB entries covers 512x more address space. This dramatically reduces TLB misses for applications with large working sets.

**Q5: (C)** Shared memory requires no kernel involvement for data access after setup — processes read/write directly to the same physical memory region. All other mechanisms involve system calls, buffer copies, or protocol overhead.

**Q6: (B)** `isolcpus` tells the CFS scheduler not to place any task on the specified CPUs. Only tasks explicitly pinned to those CPUs (via `taskset` or `sched_setaffinity`) will run on them. This prevents OS housekeeping from causing latency spikes.

**Q7: (B)** SCHED_FIFO is a real-time policy where the highest-priority runnable task always runs immediately, preempting any lower-priority task (including all CFS tasks). There's no time slicing at the same priority level. This provides the most deterministic latency for trading applications.

**Q8: (B)** `strace` intercepts and logs all system calls made by a process (open, read, write, mmap, etc.) along with arguments and return values. `ltrace` traces library calls. `perf` provides CPU-level profiling.

**Q9: (B)** `O_DIRECT` bypasses the kernel's page cache. Reads go directly from disk to the user buffer; writes go directly from user buffer to disk. The buffer must be aligned to the filesystem block size (typically 512 bytes or 4 KB). This prevents page cache pollution but loses the benefit of caching.

**Q10: (C)** Remote memory access (crossing the QPI/UPI interconnect to another socket) is approximately 1.5-2x slower than local memory access. For a trading application, accessing remote memory adds ~50-100ns of latency per access, which compounds across millions of accesses.

**Q11:** `perf stat` runs a command and prints summary CPU counter statistics (instructions, cycles, cache misses, IPC, branch mispredictions). Use it for a quick health check. `perf record` samples the call stack at regular intervals during execution, then `perf report` shows which functions consume the most CPU time. Use `perf record` when you need to identify specific hot functions.

**Q12:** The page cache keeps recently read/written file data in memory. Subsequent reads hit the cache instead of disk (microseconds vs. milliseconds). It helps most applications because repeated file access is common. It hurts when: (a) you're streaming large files that won't be re-read (wastes memory, evicts useful data), (b) you need deterministic write latency (dirty page writeback is asynchronous and bursty), (c) you're using `O_DIRECT` for specific performance reasons.

**Q13:** 1) Application calls `write(fd, buf, len)`. 2) Trap to kernel (syscall). 3) Kernel copies data from userspace buffer to kernel socket send buffer. 4) TCP stack adds headers, creates segments. 5) IP layer adds IP header, passes to device driver. 6) Driver copies data to NIC's DMA ring buffer (or NIC DMAs from kernel buffer). 7) NIC transmits on wire. That's at least 2 copies (user to kernel, kernel to NIC) with standard networking.

**Q14:** IRQ affinity controls which CPU handles a specific hardware interrupt. For trading: set NIC interrupts to a dedicated CPU (separate from the trading application's CPU). This prevents NIC interrupts from preempting the trading thread. Without affinity, an interrupt could arrive on the trading core, causing a ~5-10us latency spike while the interrupt handler runs.

**Q15:** `nohz_full` disables timer tick interrupts on specified CPUs when only one task is running. Normally, the kernel sends a timer interrupt every 1-4ms (HZ=250/1000) to each CPU for scheduling. For a latency-sensitive application pinned to a dedicated core, these ticks are useless overhead (~1us each) that can cause jitter.

**Q16:** SIGTERM (15) can be caught and handled — the process can perform cleanup (cancel orders, close FIX sessions, flush logs). SIGKILL (9) cannot be caught — the process is terminated immediately. A trading application MUST handle SIGTERM to gracefully unwind positions and close exchange sessions. Being killed without cleanup could leave orphaned orders on the exchange.

**Q17:** High context switch rate indicates many tasks competing for CPU time, or many blocking I/O operations causing task switches. Each context switch costs ~1-10us directly plus cache pollution. For a trading application, this means unpredictable latency. Causes: too many threads, excessive I/O, poor CPU pinning. Solution: reduce thread count, pin critical threads to isolated cores, use non-blocking I/O.

**Q18:** After `fork()`, parent and child share the same physical memory pages, but the pages are marked read-only (copy-on-write). When either process attempts to WRITE to a shared page, the CPU triggers a page fault. The kernel then: (1) allocates a new physical page, (2) copies the contents of the original page, (3) updates the writing process's page table to point to the new page, (4) marks both pages as writable. This makes fork() fast (no copying until needed) and memory-efficient (unmodified pages remain shared).
