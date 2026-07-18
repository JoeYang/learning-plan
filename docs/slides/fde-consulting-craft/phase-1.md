# Discovery & scoping

Stakeholder interviews, use-case disqualification, and ROI framing — the round that decides whether the rest of the engagement solves the right problem.

> **The theme:** engineers lose FDE loops by pitching solutions into an unscoped problem. Discovery is not small talk before the real work — it *is* the real work. The output is a one-page brief a skeptical sponsor would sign: problem, disqualified alternatives, scoped use case, measurable success criteria.

---

<!-- class: is-section -->

# Part one — the discovery funnel

Ask before you build. In order.

---

## The problem — the stated ask is rarely the real problem

A Head of Research says: *"our analysts drown in filings — help."*

What they might actually need:

- a **triage** problem — which 5 of 400 filings matter today
- a **synthesis** problem — the reading is fine, the cross-referencing is slow
- a **process** problem — three teams read the same filings and don't share notes
- a **coverage** problem — they miss filings entirely and find out from clients

Build a filings chatbot for the first framing when the truth is the third, and the engagement fails *after* you've shipped. Discovery exists to find which problem you're in **before** anything is scoped.

---

## The challenge — solution-first bias

The failure modes discovery defends against, in the order they usually strike:

- **Pitching in the first ten minutes** — the moment you propose, the client stops disclosing and starts evaluating
- **Accepting the stated problem** — "we need a chatbot" is a solution wearing a problem costume
- **Unmeasurable success** — "analysts feel more productive" cannot close an engagement
- **Wrong room** — scoping with someone who can't say yes (or worse, can't say no)

Every one of these feels productive in the moment. That's what makes them dangerous.

---

## The solution — a funnel with four gates

```
  open problem questions      "walk me through yesterday's filing workflow"
        │
  constraint surfacing        latency? data access? compliance? budget owner?
        │
  disqualification            should this even be an AI project?
        │
  success criteria            what number moves, by when, measured how?
```

Order matters: constraints before disqualification (you can't rule out what you haven't sized), disqualification before success criteria (don't define victory for a project that shouldn't exist).

---

## The solution — SPIN, adapted not recited

SPIN (Rackham) is a questioning sequence, not a script. Adapted to a finance-vertical FDE conversation:

| Stage | Sales original | FDE adaptation |
|---|---|---|
| **S**ituation | "what's your current setup?" | "who reads which filings today, in what tool?" |
| **P**roblem | "what's not working?" | "where did the process last visibly fail?" |
| **I**mplication | "what does that cost you?" | "what did missing that 8-K cost the desk?" |
| **N**eed-payoff | "what would fixing it be worth?" | "if triage took 20 minutes, what changes downstream?" |

The adaptation rule: every question should be answerable with an *observable fact*, not an opinion about software.

---

<!-- class: is-section -->

# Part two — disqualification & ROI

Saying no is a deliverable.

---

## The checklist — what should NOT be an AI project

Disqualify a candidate use case when any of these holds:

- **No ground truth** — nobody can say what a correct output looks like, so nothing can be evaluated
- **Unmeasurable success** — the win can't be observed within a quarter
- **The bottleneck is organisational** — a model can't fix three teams refusing to share notes
- **Latency kills it** — the workflow needs an answer in microseconds; LLM inference is milliseconds at best
- **Stakes exceed error tolerance** — a wrong answer is a regulatory event, and there's no human-in-the-loop budget

A written disqualification with reasoning builds more trust than a demo. It proves you're spending their money like it's yours.

---

## ROI framing — speak the buyer's language

Three narrative shapes, matched to what a finance sponsor already worries about:

- **Cost avoidance** — "four analysts × 3 hours of filing triage daily; automation returns ~60 analyst-hours a week"
- **Revenue lift** — "coverage of mid-cap filings doubles; the desk catches earnings surprises it currently misses"
- **Risk reduction** — "no filing goes unread past 24 hours; compliance gets an audit trail"

Two different pitches for two different people:

- the **economic buyer** (owns budget) hears the narrative above
- the **technical champion** (owns the workflow) hears architecture, evals, and integration effort

MEDDIC's useful residue for FDE work: always know which of the two you're talking to, and never confuse the metric *they* care about with the one you'd put on a dashboard.

---

## Validation — how you know discovery worked

The phase capstone is `discovery-scoping-brief.md`, and it passes review when:

- success criteria are **measurable within one quarter** — a number, a baseline, a deadline
- at least one candidate use case is **disqualified on the record**, with reasoning
- the stakeholder map names the economic buyer, champion, end users, and likely blockers
- the ROI narrative reads in the buyer's language — no embeddings, no rerankers, no token counts
- an engineer who wasn't in the room could pick up the brief and scope Phase 2 from it

Session 1 builds the transcript and the disqualification; Session 2 builds the metrics, the map, and the brief itself.
