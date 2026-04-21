# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A personal learning tracker. The content layer is markdown; a small Python tool (`.claude/skills/axiom-design/render-slides.py`, stdlib only) converts markdown source into HTML slide decks. No package manager for the core, just git; the optional `axiom-viz` skill brings its own Node deps.

## Structure

- `topics/` — Topic definitions (copy `_template.md` to create new ones)
- `plans/` — Day-by-day learning plans (one per topic)
- `log/` — Session reflections (`YYYY-MM-DD.md`) — Claude drafts, Joe edits
- `quizzes/<topic>/` — Per-session quizzes and results
- `artefacts/<topic>/phase-N/` — Capstone deliverables that prove mastery
- `docs/slides/<topic>/` — Per-phase slide-deck markdown source (rendered to HTML)
- `docs/interactive/<topic>/` — Interactive explainer pages for dynamic concepts
- `.claude/skills/axiom-design/` — design tokens, deck-stage.js, and `render-slides.py` (plus tests)
- `completed/` — Archive for finished topics and plans
- `PROGRESS.md` — Central dashboard with active/completed topic tables and `Last Activity` column
- `.claude/launch.json` — `static-server` config (`python3 -m http.server 8000`) for previewing decks

## Conventions

- Filenames: kebab-case (e.g., `cpp-trading-systems.md`)
- Dates: YYYY-MM-DD everywhere
- Plan checkboxes: `- [ ]` for pending, `- [x]` for done
- When creating a new topic, match the format in `topics/_template.md`
- When creating a new plan, match the format in existing plans (header metadata, day-by-day sections with objectives, checkboxes, key concepts, resources)
- When updating progress, update both the plan checkboxes and the `PROGRESS.md` dashboard table (days done, percentage, next session)

## Workflow

### Session structure: Pre-read → Apply → Prove

Every session runs through three steps in order. Do not skip the Pre-read.

1. **Pre-read** — Before the session, check `docs/slides/<topic>/phase-N.md` for the phase deck. If it exists, render it (`python3 .claude/skills/axiom-design/render-slides.py docs/slides/<topic>/phase-N.md docs/slides/<topic>/phase-N.html`) and remind Joe to open it at http://localhost:8000/docs/slides/<topic>/phase-N.html. If the deck is missing for the current phase, generate the markdown source first (one deck per phase, not per session — decks summarise the phase's key concepts in 5–10 slides).
2. **Apply** — Walk Joe through the session's checkboxed exercises as in the plan file.
3. **Prove** — Run the session quiz (rules below). If the session closes a phase, prompt Joe to increment the capstone deliverable in `artefacts/<topic>/phase-N/` — the session isn't "done" until there's a capstone artefact that proves mastery.

### Marking sessions done

Only after all three steps above: update `- [ ]` to `- [x]` in the plan file, increment "Days Done" in `PROGRESS.md`, update the percentage, advance "Next Session", and update the "Last Activity" column to today's date.

### Session log (Claude drafts, Joe edits)

At session end, draft a 3–5 line entry in `log/YYYY-MM-DD.md` covering:
- **Learned:** the one thing that actually clicked
- **Blocked:** the one thing that didn't click (or empty)
- **Next:** the focus for the next session

Show the draft to Joe and ask him to confirm/edit before writing the file. The goal is a low-friction reflection ritual that spots patterns week-over-week — not a full journal.

### When a phase closes: schedule a retrieval check

When Joe marks the last session of a phase as done, use the `scheduled-tasks` MCP tool (`mcp__scheduled-tasks__create_scheduled_task`) to schedule a 7-day retrieval check:

- `taskId`: `retrieval-check-<topic>-phase-<N>`
- `fireAt`: 7 days from today at 09:00 local
- `prompt`: "Run a 3-question retrieval check for <topic> Phase <N>. Pick 3 questions from quizzes/<topic>/phase-<N>/ without revealing answers. Ask Joe to answer from memory. Grade, log the result to `log/<date>.md`."

This turns the 7-day check from a good intention into a scheduled event.

### Adding a new topic

Create both `topics/<name>.md` (including the Capstone field) and `plans/<name>.md` with per-phase capstone lines, add a row to the Active Topics table in `PROGRESS.md` with today's date as "Last Activity".

### Completing a topic

Move files to `completed/topics/` and `completed/plans/`, archive `artefacts/<topic>/` unchanged (it's the record of what was learned), and move the row from Active to Completed in `PROGRESS.md`.

## Session Quiz

After each session, offer a 10-question interactive quiz using the AskUserQuestion tool (one question at a time).

### Composition

- **7 multiple-choice + 2–3 short-answer.** Short-answer = Joe types a free-form response; grade against a rubric (key concepts that must appear). This kills the "longest-option" heuristic.
- **Mix of question types:** conceptual, applied-scenario, trade-off ("given these constraints, which approach wins?"), and at least one **"subtly wrong"** question (three options look right; one has a small error Joe must catch).
- Scenarios should follow the V2 diagnostic pattern from `plans/claude-certified-architect.md`: a scenario with constraints → distractors that all "work" but only one is "best given constraints."

### Answer formatting rules (enforced before showing the quiz)

Before presenting the quiz, self-audit against these rules. If any fail, regenerate the offending questions:

1. **Length normalisation:** all four options within ±20% character count of each other. If the correct answer is longer, pad the distractors with plausible specifics; don't trim the correct answer to something evasive.
2. **Correct-answer distribution:** across the quiz, the correct answer position should be roughly uniform across A/B/C/D. If any position is the correct answer for more than ~35% of questions, reshuffle.
3. **Longest-option check:** the correct answer is the longest option in no more than ~30% of questions. If higher, rewrite.
4. **No giveaway phrasing:** strip "always", "never", "all of the above" from distractors unless they are genuinely correct — these are tells.

### Feedback & scoring

- After each answer, give immediate feedback with a brief explanation (whether correct or not).
- For short-answer: show the rubric, mark which rubric points Joe hit, and give credit accordingly (full / half / none).
- At the end, report the final score (e.g., 8/10) and note any weak areas to review.
- If Joe scores below 7/10, suggest reviewing the missed topics before the next session.

### Capstone requirement

The quiz proves recall and reasoning. The **capstone** proves he can apply it. At the end of each phase, remind Joe that the phase isn't closed until a capstone artefact exists in `artefacts/<topic>/phase-N/`. Examples: a working `.cpp` demonstrating the phase's concepts, a backtest notebook with a written trade-off reflection, a scenario design doc a peer could review. The capstone is named in the plan's `Capstone:` line for the phase.
