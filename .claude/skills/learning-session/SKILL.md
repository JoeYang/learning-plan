---
name: learning-session
description: Orchestrate a single learning session end-to-end — Pre-read (generate/open phase deck) → Apply (walk the checkboxed exercises) → Prove (interactive quiz + capstone + session log + retrieval-check scheduling). Triggers on "start session N", "run the next session", "quiz me on X", "take me through session N of <topic>". Assumes the project follows the learning-plan structure (topics/, plans/, quizzes/, artefacts/, docs/slides/).
user-invocable: true
---

# learning-session

One skill that drives a complete self-study session, start to finish. The goal is to keep the three high-value rituals on every session — pre-read, active recall, proof of mastery — without the learner having to remember to run each one.

## When to use this skill

- **"start session 6"** or **"run the next session"** — default trigger.
- **"quiz me on <topic>"** — Prove-only path; skip Pre-read and Apply.
- **"walk me through session N"** — full flow.

## Preconditions

The project must have the learning-plan layout:

```
<repo>/
├── topics/<topic>.md            # topic definition + Capstone field
├── plans/<topic>.md             # day-by-day plan with phases & sessions
├── quizzes/<topic>/             # per-session quizzes and results
├── artefacts/<topic>/phase-N/   # capstone deliverables
├── docs/slides/<topic>/         # per-phase slide-deck markdown
├── log/YYYY-MM-DD.md            # per-day session reflections
└── PROGRESS.md                  # dashboard
```

If any of these are missing, create them before the first session.

## Required companion skills

- **`axiom-design`** — for `render-slides.py`; used in Pre-read.
- **`axiom-viz`** — when a concept needs interactive motion rather than a slide.
- **`interactive-visual`** — for single-file HTML explainer pages saved to `docs/interactive/<topic>/`.

## The flow

### 1. Pre-read — prepare and open the phase deck

1. Identify the current session from `plans/<topic>.md` (first unchecked `- [ ]` header).
2. Determine the phase it belongs to.
3. Check `docs/slides/<topic>/phase-N.md` — does a deck exist for this phase?
   - **If missing**: synthesise 5–10 slides from the plan's teach blocks and the notes in `docs/notes/` for that phase. One concept per slide. Use the Axiom markdown conventions from `.claude/skills/axiom-design/AXIOM_README.md`: sentence case, em-dashes, Unicode math (→ ≤ ≠), no emoji. Write the file.
   - **If present**: skip to render.
4. Render the deck:
   ```
   python3 .claude/skills/axiom-design/render-slides.py \
     docs/slides/<topic>/phase-N.md \
     docs/slides/<topic>/phase-N.html \
     --eyebrow "<topic> · phase N"
   ```
5. Ensure `static-server` from `.claude/launch.json` is running; prompt Joe to open http://localhost:8000/docs/slides/<topic>/phase-N.html.
6. Pause here and wait for him to confirm he's read it before moving on.

### 2. Apply — walk the session exercises

1. Read the current session block from `plans/<topic>.md`.
2. For each `- [ ]` checkbox, talk through the concept, ask Joe to answer or apply it, and flip to `- [x]` only once he actually responds correctly or demonstrates it.
3. If a concept is genuinely dynamic (memory layout, tree traversal, animated flow), offer to spin up `axiom-viz` (`npm --prefix .claude/skills/axiom-viz run dev`, http://localhost:5173) rather than explaining in text. For static-but-visual concepts prefer a slide.
4. Keep notes of anything Joe got wrong on first pass — these feed the quiz below.

### 3. Prove — interactive quiz

Use the `AskUserQuestion` tool to present the quiz one question at a time.

Structure (10 questions):
- 7 multiple-choice + 2–3 short-answer (free-text graded against a rubric).
- Mix conceptual, applied-scenario, trade-off, and at least one "subtly wrong" question (three options look right; one has a small error).
- Scenarios with constraints. Distractors all "work" — only one is "best given constraints."

Self-audit BEFORE presenting the quiz (enforce, don't just aspire):
- **Length normalisation**: all four options within ±20% character count. Pad distractors with plausible specifics — don't shorten the correct answer.
- **Correct-answer distribution**: roughly uniform across A/B/C/D. No position > ~35%.
- **Longest-option check**: correct answer is longest in ≤ ~30% of questions.
- **Strip giveaways**: no "always", "never", "all of the above" unless genuinely correct.

Grading:
- Immediate feedback with a short explanation after each answer.
- Short-answer: show the rubric, mark which points were hit, give full/half/none credit.
- Final score + weak areas.
- If < 7/10, suggest revisiting the failed topics before the next session.

### 4. Capstone (only when this session closes a phase)

1. Re-read the `Capstone:` line for this phase in `plans/<topic>.md`.
2. Prompt Joe to finish the capstone artefact in `artefacts/<topic>/phase-N/`.
3. Do NOT mark the session `- [x]` in the plan until the capstone exists.

### 5. Schedule 7-day retrieval check (only when this session closes a phase)

Use `mcp__scheduled-tasks__create_scheduled_task` with:

- `taskId`: `retrieval-check-<topic>-phase-<N>`
- `fireAt`: 7 days from today at 09:00 local
- `prompt`: `"Run a 3-question retrieval check for <topic> Phase <N>. Pick 3 questions from quizzes/<topic>/phase-<N>/ without revealing answers. Ask Joe to answer from memory. Grade, log the result to log/<today>.md."`

### 6. Session log

Draft a 3–5 line entry in `log/YYYY-MM-DD.md`:

- **Learned**: the one thing that actually clicked.
- **Blocked**: the one thing that didn't click (or empty).
- **Next**: the focus for the next session.

Show the draft to Joe and ask him to confirm/edit before writing.

### 7. Mark done and advance

Only now, after all six steps above:

- Tick the session's `- [ ]` → `- [x]` in `plans/<topic>.md`.
- Update `PROGRESS.md`: increment Days Done, bump percentage, advance Next Session, set Last Activity to today.
- Commit on a branch named `feat/progress-<topic>-session-<N>`.

## Anti-patterns to avoid

- **Skipping Pre-read** when the deck is missing — the whole point is the deck gets generated on demand, not later.
- **Marking a session done without the quiz** — box-ticking returns.
- **Marking a phase-closing session done without the capstone** — evidence layer collapses.
- **Hand-authoring the quiz without the self-audit** — length-based gaming creeps back in.
- **Inventing retrieval-check cadence manually** — use scheduled-tasks or it won't happen.

## What to do if the user just says "quiz me"

Skip Pre-read and Apply. Ask which topic + phase + session range. Run step 3 only. Do NOT create a log entry or mark anything done.
