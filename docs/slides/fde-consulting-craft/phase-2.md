# The 45-minute drill

A vague customer prompt, a timer, and a blank page — the signature FDE case-study round, drilled three times at escalating difficulty.

> **The theme:** there is no "right" answer — the round tests whether you impose *structure on ambiguity* under time pressure: assumptions stated, scope bounded, milestones real, risks named. Roughly 30% of loop weight rides on this round.

---

## The problem — ambiguity is the job

The prompt arrives exactly like this, and no more:

> *"Our analysts drown in filings — help."*

No org chart, no data inventory, no budget, no success criteria. In a real engagement you'd have a week of discovery; in the interview room you have 45 minutes to produce a plan a hiring panel can poke at. The skill being measured is decomposition — the same one Phase 1 built, compressed under a clock.

---

## The challenge — how candidates actually fail

Five failure modes account for most rejections in this round:

- **Boiling the ocean** — scoping a platform when the prompt needs a wedge
- **Silent assumptions** — building on unstated guesses the panel can't see or challenge
- **Task lists instead of milestones** — "set up RAG, add evals" is activity, not progress anyone can verify
- **Picking sides silently** — when stakeholders conflict, choosing one without surfacing the tension
- **Swallowing unrealistic constraints** — accepting "by next month, no data" without pushing back

Notice none of these are knowledge gaps. They're structure gaps — which is why this phase is pure reps.

---

## The solution — a fixed time structure

Forty-five minutes, four boxes, no extensions:

```
   0–5 min    clarify        state assumptions out loud; pick the problem framing
   5–20 min   scope          one wedge use case, explicit boundary, architecture sketch
  20–35 min   plan           3–4 milestones with verifiable exit criteria
  35–45 min   risks + next   top failure modes, what discovery would confirm, week-one steps
```

The structure is the safety net: when the clock erodes judgement, the boxes tell you what you owe next. Practising the *transitions* matters more than practising any single box.

---

## Worked example — decomposing the filings prompt

One defensible 45-minute output for the baseline prompt, compressed:

- **Assumptions (stated):** research desk at a bank; ~400 filings/day across coverage; analysts triage manually; no labeled data exists; augmentation, not replacement
- **Scope boundary:** filing **triage and summarisation** for one sector team — *not* Q&A, *not* trade recommendations, *not* firm-wide rollout
- **Milestones:** (1) corpus + ingestion for one sector, verified against a week of real filings — (2) triage ranking with analyst feedback loop, measured against analyst picks — (3) summary generation with citation checks, graded weekly — (4) pilot with 3 analysts, exit on time-saved measurement
- **Risks:** no ground truth for "important filing" → mitigate with analyst-labelled feedback from week one; hallucinated numbers → citations mandatory; adoption risk → the pilot analysts co-design the ranking signals

The panel doesn't need this to be *their* answer — they need every choice to be visibly reasoned.

---

## The rubric — written once, used three times

Session 3 writes it; every drill is graded against it immediately after the timer:

1. assumptions stated **explicitly**, before scoping begins
2. scope has a **clear boundary** — something obvious is deliberately out
3. at least one **disqualified alternative** noted, with a reason
4. the plan has **milestones with exit criteria**, not a task list
5. risks name a **real failure mode** — not "timeline risk"

Drill 3 adds a sixth: the plan **pushes back on at least one unrealistic constraint** with a stated reason, rather than silently accepting it.

---

## Escalation — three drills, three pressures

- **Drill 1 (Session 3), baseline:** the filings prompt, cold. Establishes pacing — where did the 45 minutes actually go?
- **Drill 2 (Session 4), conflicting stakeholders:** ops wants "automation", compliance wants a human on everything, budget unstated. Graded on whether the tension is surfaced *explicitly* — the plan reconciles or sequences it, never silently picks a side.
- **Drill 3 (Session 5), adversarial constraints:** chatbot "by next month", no labeled data, replace-the-analysts framing. Graded on credible push-back — augmentation reframe, a realistic wedge, and a stated reason for each rejected constraint.

Between drills: a written retro — *what took too long, what gets cut first next time*. The retro is what turns three attempts into a trend instead of three isolated performances.

---

## Validation — what "better" looks like by drill 3

The phase closes when `drill-1.md`, `drill-2.md`, `drill-3.md` all exist, each with its timed output and self-review. Across the three, the trend to look for:

- clarify-box discipline becomes automatic — assumptions land in the first five minutes without prompting
- the scope boundary appears **earlier** each drill and survives the whole plan
- rubric scores rise while the *time to first milestone written* falls
- the consolidated retro can name, specifically, what is now automatic and what still burns clock

That trend — not any single drill's output — is what transfers to the real interview room.
