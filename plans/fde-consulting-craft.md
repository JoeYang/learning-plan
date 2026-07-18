# Learning Plan: FDE Consulting Craft — The Consultant Half of Forward Deployed Engineering

**Start date:** 2026-07-20
**Target completion:** 2026-12-20
**Schedule:** 1 session/week, interleaved with the technical FDE tracks
**Status:** not-started

> Approach: Reps over reading. This is a performance skill, not a knowledge domain — nobody got better at live demos or 45-minute scoping drills by reading about them. Every session ends in a graded performance artefact (a recording, a written document, or a timed drill output scored against a rubric), never a quiz score. The 5-month span with 1 session/week is intentional spaced repetition: discovery, scoping, demo craft, and written artefacts need to decay and get re-triggered under mild pressure, not be crammed.

---

## Capstones by Phase

Each phase closes with a concrete performance artefact committed to `artefacts/fde-consulting-craft/phase-N/`. A phase isn't closed until its capstone exists.

| Phase | Capstone |
|---|---|
| Phase 1 (Discovery & Scoping) | `artefacts/fde-consulting-craft/phase-1/discovery-scoping-brief.md` — written discovery brief for a fictional financial-services client with stakeholder map, disqualified use cases, and ROI framing |
| Phase 2 (Ambiguous Case-Study Drills) | `artefacts/fde-consulting-craft/phase-2/drill-1.md`, `drill-2.md`, `drill-3.md` — three timed 45-minute scoped-plan outputs, each self-reviewed against a rubric |
| Phase 3 (Demo Craft) | `artefacts/fde-consulting-craft/phase-3/demo-take-1.md` and `demo-take-2-hostile-qa.md` — recorded demo takes (links) with narrative structure, a recovered live failure, and a handled hostile question |
| Phase 4 (Written Artifacts + Mock Engagement) | `artefacts/fde-consulting-craft/phase-4/solution-brief.md`, `sow-lite.md`, `mock-engagement.md` — full mock engagement dry run: discovery call → scoped plan → 10-min demo → follow-up brief |

## Phase 1: Discovery & Scoping (Sessions 1–2)

Discovery is the round most engineers skip in prep and the one that decides whether the rest of the engagement is solving the right problem. This phase drills stakeholder interviews, disqualifying bad AI-project candidates, and framing ROI for a non-technical sponsor, using finance-vertical scenarios (a bank's research desk, a fund's ops team).

**Phase 1 capstone:** `artefacts/fde-consulting-craft/phase-1/discovery-scoping-brief.md`

**Visual:** `docs/slides/fde-consulting-craft/phase-1.md` — 6–10 slides on the discovery funnel (open questions → constraints → disqualification → success criteria), the "what should NOT be an AI project" checklist, and ROI framing patterns for a skeptical financial-services sponsor.

### Session 1: Stakeholder Interviews & Use-Case Selection
**Objective:** Run a structured discovery conversation that surfaces the real problem and rules out bad AI-project candidates before scoping begins.
- [ ] Study the discovery funnel: open-ended problem questions → constraint-surfacing questions → success-criteria questions
- [ ] Study SPIN (Situation, Problem, Implication, Need-payoff) and adapt 2–3 questions per stage to a finance-vertical scenario
- [ ] Build a "what should NOT be an AI project" checklist (e.g., no ground-truth data, success criteria unmeasurable, real bottleneck is a process/org issue, latency requirement makes LLM inference a non-starter)
- [ ] Draft a fictional persona: Head of Research at a mid-size asset manager, frustrated that analysts "drown in filings"
- [ ] Role-play the discovery conversation solo, both sides (interviewer + persona), written or recorded
- [ ] Identify at least one candidate use case in the transcript that should be disqualified, and write the disqualification reasoning
- [ ] Identify at least one candidate use case worth scoping further
- [ ] **Record a 5-minute audio/video walkthrough** of the discovery transcript: what you'd ask next, and why the disqualified use case fails
- [ ] Self-review the recording against a rubric: did you ask open questions before proposing solutions? did you surface a real constraint? did you avoid pitching a solution before the problem was scoped?
**Key concepts:** discovery funnel, SPIN adaptation, AI-project disqualification criteria, stakeholder persona construction
**Resources:** SPIN Selling (Rackham) — adapted, not used as a script; Palantir FDE writeups on discovery-round expectations; *The Trusted Advisor* ch. 1–3 on earning the right to ask hard questions

### Session 2: ROI Framing & Success-Criteria Definition
**Objective:** Translate a scoped use case into an ROI narrative and measurable success criteria a non-technical sponsor would sign off on.
- [ ] Study ROI framing patterns: cost-avoidance vs. revenue-lift vs. risk-reduction narratives, and when each applies to a finance buyer
- [ ] Study MEDDIC (Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion) — adapt the "Metrics" and "Economic Buyer" components to a technical scoping brief
- [ ] For the Session 1 use case (analysts drowning in filings), draft 3 candidate success metrics and stress-test each for measurability
- [ ] Identify the economic buyer vs. the technical champion in the fictional org and note how the pitch differs for each
- [ ] Draft a stakeholder map: economic buyer, technical champion, end users, blockers
- [ ] Write the discovery + scoping brief combining Session 1 and Session 2 outputs: problem statement, disqualified alternatives, scoped use case, success criteria, ROI narrative, stakeholder map
- [ ] Self-review against a rubric: is the ROI narrative in the buyer's language, not engineering language? are success criteria measurable within one quarter?
- [ ] **Write the one-page discovery-scoping-brief.md** — this is the Phase 1 capstone
**Key concepts:** ROI narrative types, MEDDIC adaptation, economic buyer vs. champion, measurable success criteria
**Resources:** MEDDIC overview (adapted for technical scoping, not quota-carrying sales); *The Trusted Advisor* ch. 4–6 on framing value; Pragmatic Engineer FDE issues on how Palantir FDEs pitch ROI to non-technical sponsors

---

## Phase 2: Ambiguous Case-Study Drills (Sessions 3–5)

This is the signature FDE interview round: a vague customer prompt like "our analysts drown in filings — help" arrives with no scoping, and the candidate has 45 minutes to produce a defensible plan. Three timed drills, escalating difficulty, each graded against a written rubric — this phase is pure reps, not teaching.

**Phase 2 capstone:** `artefacts/fde-consulting-craft/phase-2/drill-1.md`, `drill-2.md`, `drill-3.md`

**Visual:** `docs/slides/fde-consulting-craft/phase-2.md` — 6–10 slides on the 45-minute drill structure (clarify → scope → plan → risks → next steps), a worked example decomposition, and the self-review rubric used across all three drills.

### Session 3: Timed Drill 1 — Baseline Difficulty
**Objective:** Decompose a vague, single-sentence prompt into a scoped plan within a 45-minute timer, establishing a baseline.
- [ ] Study the 45-minute drill structure: 5 min clarify assumptions, 15 min scope + architecture sketch, 15 min plan + milestones, 10 min risks + next steps
- [ ] Write the self-review rubric once (reused across all three drills): assumptions stated explicitly, scope has a clear boundary, at least one disqualified alternative noted, plan has milestones not just a task list, risks section names a real failure mode
- [ ] Set a 45-minute timer
- [ ] **45-minute timed drill:** given the prompt "our analysts drown in filings — help" (a bank research desk), produce a written scoped plan
- [ ] Stop at the timer, no extensions
- [ ] Self-review the output against the rubric immediately after, noting where you ran out of time
- [ ] Write a short retro: what took too long, what you'd cut first under time pressure next time
- [ ] Save the timed output and self-review as `drill-1.md`
**Key concepts:** 45-minute drill cadence, assumption-stating discipline, scope boundary-setting under time pressure
**Resources:** Exponent FDE interview guide (case-study round format and sample prompts); Palantir FDE loop retrospectives (Blind/Glassdoor summaries) for calibration on real prompt difficulty

### Session 4: Timed Drill 2 — Escalated Ambiguity
**Objective:** Repeat the timed drill against a harder, more ambiguous prompt with conflicting stakeholder signals, applying lessons from the Session 3 retro.
- [ ] Review the Session 3 retro before starting — name the one habit to fix this round
- [ ] Set a 45-minute timer
- [ ] **45-minute timed drill:** given a harder prompt with conflicting signals (a fund's ops team wants "automation" but the compliance lead wants a human-in-the-loop on everything, and budget is unstated), produce a written scoped plan
- [ ] Stop at the timer, no extensions
- [ ] Self-review against the same rubric from Session 3
- [ ] Specifically grade: did the plan surface the compliance/automation tension explicitly, or silently pick a side?
- [ ] Write a short retro comparing this drill's pacing to Session 3's
- [ ] Save the timed output and self-review as `drill-2.md`
**Key concepts:** conflicting-stakeholder scoping, human-in-the-loop trade-offs, pacing consistency across repeated drills
**Resources:** Exponent FDE interview guide; MEDDIC's "Decision Process" component applied to reconciling conflicting stakeholders

### Session 5: Timed Drill 3 — Adversarial Constraints
**Objective:** Repeat the timed drill under adversarial constraints (unrealistic deadline, missing data access, a stakeholder who wants the wrong solution) and demonstrate the plan pushes back where warranted.
- [ ] Review the Session 4 retro before starting
- [ ] Set a 45-minute timer
- [ ] **45-minute timed drill:** given an adversarial prompt (a research desk head wants a chatbot "by next month," has no labeled data, and insists on replacing analysts rather than augmenting them), produce a written scoped plan
- [ ] Stop at the timer, no extensions
- [ ] Self-review against the rubric, plus a new criterion: does the plan push back on at least one unrealistic constraint with a stated reason, rather than silently accepting it?
- [ ] Write a consolidated retro across all three drills: what's still slow, what's now automatic
- [ ] Save the timed output and self-review as `drill-3.md`
- [ ] Confirm all three drill artefacts exist in `artefacts/fde-consulting-craft/phase-2/` — this closes Phase 2
**Key concepts:** pushing back on unrealistic constraints, augmentation vs. replacement framing, cross-drill pacing trend
**Resources:** Palantir FDE writeups on handling adversarial interviewer pressure; *The Trusted Advisor* ch. 7 on saying no credibly

---

## Phase 3: Demo Craft (Sessions 6–7)

A scoped plan means nothing if the live demo falls apart in front of the client. This phase drills narrative structure (problem → stakes → resolution), live-demo discipline, recovering from failure without losing composure, and handling hostile questions — producing recorded demo takes as proof.

**Phase 3 capstone:** `artefacts/fde-consulting-craft/phase-3/demo-take-1.md`, `demo-take-2-hostile-qa.md`

**Visual:** `docs/slides/fde-consulting-craft/phase-3.md` — 6–10 slides on the problem-stakes-resolution narrative arc, the Great Demo! "illustrate the last mile" method, a live-failure recovery checklist, and a hostile-question response framework.

### Session 6: Narrative Structure & Live-Demo Discipline
**Objective:** Deliver a recorded demo with a problem → stakes → resolution narrative and recover cleanly from at least one injected live failure.
- [ ] Study the problem → stakes → resolution narrative arc and why demos that open with features instead of stakes lose the room
- [ ] Study Great Demo!'s "illustrate the last mile" — show the specific moment of value, not the whole product tour
- [ ] Pick the system from `topics/fde-production-ai-systems.md` (or a stand-in) as the demo subject
- [ ] Script a 5-minute demo narrative: the analyst's problem, what's at stake if unsolved, the resolution moment
- [ ] Deliberately inject one live failure into the demo run (a bad query, a tool timeout, an empty result) and rehearse the recovery line
- [ ] **Record a 5-minute demo take** end to end, including the injected failure and recovery
- [ ] Self-review against a rubric: did the narrative open with stakes, not features? was the failure recovery calm and forward-moving rather than apologetic?
- [ ] Save the recording link and self-review as `demo-take-1.md`
**Key concepts:** problem-stakes-resolution arc, illustrate-the-last-mile, live-failure recovery discipline
**Resources:** *Demo2Win* / Great Demo! (Peter Cohan) — full method; Pragmatic Engineer FDE issues on demo expectations in forward-deployed roles

### Session 7: Handling Hostile Questions
**Objective:** Deliver a second recorded demo take that includes a hostile or skeptical question mid-demo, and handle it without losing the room.
- [ ] Study patterns for hostile-question handling: acknowledge without conceding, bridge back to the stakes, offer to go deeper offline rather than derailing the demo
- [ ] Write 3 hostile questions a skeptical finance client might ask (e.g., "how do I know this isn't hallucinating the number that just appeared," "what happens when your vendor's API is down during market open," "why wouldn't I just build this in-house")
- [ ] Draft a bridge-back response for each, grounded in real answers from `topics/fde-production-ai-systems.md` work (evals, tracing, cost/latency trade-offs) — not deflection
- [ ] Re-run the Session 6 demo script with a colleague/self-prompt injecting one hostile question at an unscripted moment
- [ ] **Record a second 5-minute demo take** including the unscripted hostile question and your live response
- [ ] Self-review against a rubric: did you acknowledge the question's legitimacy before bridging? did you avoid getting defensive or over-promising?
- [ ] Save the recording link and self-review as `demo-take-2-hostile-qa.md`
- [ ] Confirm both demo-take artefacts exist in `artefacts/fde-consulting-craft/phase-3/` — this closes Phase 3
**Key concepts:** acknowledge-bridge-redirect, grounding pushback in real evidence, composure under unscripted pressure
**Resources:** *Demo2Win*; *The Trusted Advisor* ch. 8 on handling challenges to credibility; Palantir FDE loop retrospectives on hostile-interviewer demo rounds

---

## Phase 4: Written Artifacts + Mock Engagement (Sessions 8–9)

The engagement doesn't end when the demo does — it ends with a document that survives after you leave the room. This phase drills solution-brief and SOW-lite writing, then runs a full mock engagement end to end as the course capstone.

**Phase 4 capstone:** `artefacts/fde-consulting-craft/phase-4/solution-brief.md`, `sow-lite.md`, `mock-engagement.md`

**Visual:** `docs/slides/fde-consulting-craft/phase-4.md` — 6–10 slides on solution-brief structure, SOW-lite essentials (scope, milestones, exclusions, success criteria), and the end-to-end mock-engagement flow.

### Session 8: Solution Brief & SOW-Lite Writing
**Objective:** Write a one-page solution brief and a lightweight SOW that both a technical lead and procurement would find credible.
- [ ] Study one-page solution-brief structure: problem, proposed approach, expected outcome, what's explicitly out of scope
- [ ] Study SOW-lite essentials: scope statement, milestones with dates, exclusions, success criteria, assumptions/dependencies
- [ ] Using the Phase 1 discovery brief and a Phase 2 drill plan as source material, draft a one-page solution brief for the fictional financial-services client
- [ ] Draft an SOW-lite for the same engagement: 3–4 milestones, explicit exclusions, success criteria tied back to Session 2's metrics
- [ ] Have a peer (or a fresh self-read after a break) check for jargon that a procurement reader wouldn't parse
- [ ] Revise both documents for length — one page each, no exceptions
- [ ] **Write the final solution-brief.md and sow-lite.md**
- [ ] Self-review against a rubric: does the SOW's scope match the brief's promise exactly, with no scope creep between the two documents?
**Key concepts:** one-page solution-brief structure, SOW-lite essentials, scope consistency across documents
**Resources:** Palantir FDE writeups on deliverable-writing expectations; *The Trusted Advisor* ch. 9 on written follow-through; sample SOW templates (finance-vertical consulting engagements)

### Session 9: Full Mock Engagement Dry Run
**Objective:** Run the entire engagement arc end to end in one sitting — discovery call, scoped plan, 10-minute demo, follow-up brief — as the course capstone.
- [ ] Block a single ~2-hour session (longer than the usual 1.5h — this is the capstone dry run)
- [ ] **Discovery call (15 min, recorded):** role-play a fresh fictional client prompt not used in earlier sessions, run the discovery funnel from Phase 1 live
- [ ] **Scoped plan (30 min, timed):** produce a written scoped plan from the discovery call output, tighter than the Phase 2 drills since discovery already happened
- [ ] **10-minute demo (recorded):** deliver the demo with problem-stakes-resolution narrative, using the Phase 3 discipline, including at least one unscripted moment
- [ ] **Follow-up brief (30 min, written):** write the one-page solution brief and SOW-lite for this specific engagement, using Session 8's structure
- [ ] Self-review the entire arc against a consolidated rubric: did each stage flow logically from the previous one, or did the plan contradict something said in discovery?
- [ ] Write a final course retro: which phase is strongest, which needs continued practice after the course ends
- [ ] **Assemble mock-engagement.md** — links to the discovery recording, scoped plan, demo recording, and follow-up brief, plus the self-review and retro
- [ ] Confirm all Phase 4 artefacts exist in `artefacts/fde-consulting-craft/phase-4/` — this closes Phase 4 and the course
**Key concepts:** end-to-end engagement flow, cross-stage consistency, self-assessment of readiness for real FDE interview loops
**Resources:** Palantir FDE interview loop retrospectives (full-loop accounts); Exponent FDE interview guide (full-loop structure); everything from Phases 1–3 synthesized
