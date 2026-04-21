# Learning Plan

A personal learning repo for tracking self-study across multiple topics with structured 2-hour daily sessions. Every session runs **Pre-read → Apply → Prove**, and every phase ends with a capstone artefact that proves mastery.

## How It Works

The content layer is markdown. A stdlib-only Python script (`.claude/skills/axiom-design/render-slides.py`) converts phase decks from markdown into HTML slides using the vendored Axiom design system. Visualisations live in a companion `axiom-viz` skill (React + Vite). The session workflow itself is packaged as the `learning-session` skill.

### Folder Structure

```
learning-plan/
├── README.md              # This file
├── CLAUDE.md              # Workflow rules (session structure, quiz rules, capstones)
├── PROGRESS.md            # Dashboard: topics, status, % complete, Last Activity
├── topics/                # One file per topic (the "input")
│   └── _template.md       # Copy this to create a new topic
├── plans/                 # Day-by-day plans (the "output"), with per-phase capstones
├── log/                   # Per-session reflections: Learned / Blocked / Next
├── quizzes/<topic>/       # Per-session quizzes and results
├── artefacts/<topic>/     # Capstone deliverables per phase (the evidence layer)
├── docs/
│   ├── slides/<topic>/    # Per-phase deck markdown (rendered to HTML)
│   └── interactive/<topic>/  # Interactive explainer pages for dynamic concepts
├── completed/             # Archive of finished topics + plans
│   ├── topics/
│   └── plans/
└── .claude/
    ├── launch.json        # Dev-server configs (static-server :8000, viz-harness :5173)
    └── skills/            # Project-scoped Claude skills — travel with the repo
        ├── axiom-design/  # Design tokens + markdown→HTML slide renderer (Python stdlib)
        ├── axiom-viz/     # Interactive React visualisations (Vite)
        ├── learning-session/  # Pre-read → Apply → Prove session orchestrator
        └── interactive-visual/  # Pattern-driven one-off HTML explainers
```

### First-time setup on a new machine

```bash
# Slides + design system: no install needed (stdlib Python only)
python3 -m http.server 8000

# Visualisations: one-time npm install inside the skill dir
cd .claude/skills/axiom-viz
npm install
npm run dev    # http://localhost:5173
```

## Workflow

### 1. Add a Topic

```bash
cp topics/_template.md topics/<topic-name>.md
```

Fill in the template with your motivation, current level, and goals. Use kebab-case for filenames (e.g., `rust-ownership.md`, `distributed-systems.md`).

### 2. Get a Plan

Ask Claude to read the topic file and generate a day-by-day learning plan:

> "Read `topics/rust-ownership.md` and generate a 2hr/day learning plan in `plans/`"

Claude will create `plans/rust-ownership.md` with daily sessions, checkboxes, and resources.

### 3. Schedule It

Claude assigns days to specific weekdays based on your active topic count. With 2-3 topics running in parallel, each topic gets 2-3 sessions per week:

- **2 topics:** Topic A on Mon/Wed/Fri, Topic B on Tue/Thu
- **3 topics:** Topic A on Mon/Thu, Topic B on Tue/Fri, Topic C on Wed/Sat

### 4. Daily Work — Pre-read → Apply → Prove

Each session runs through three steps; skipping Pre-read is the most common way sessions turn into box-ticking.

**Pre-read (10–15 min):**
Start the static server if it's not running:
```bash
python3 -m http.server 8000
# or use .claude/launch.json via your Claude Code preview tools
```
If a deck exists for the current phase, render and open it:
```bash
python3 .claude/skills/axiom-design/render-slides.py \
  docs/slides/<topic>/phase-N.md \
  docs/slides/<topic>/phase-N.html
open http://localhost:8000/docs/slides/<topic>/phase-N.html
```
If the deck is missing, ask Claude to generate the markdown source for the phase first (one deck per phase, 5–10 slides summarising key concepts).

**Apply:**
1. Open `plans/<topic-name>.md`, find your current session
2. Work through the checkboxed exercises, check them off as you go

**Prove:**
1. Take the session quiz (10 questions; see below)
2. If the session closes a phase, update the capstone in `artefacts/<topic>/phase-N/`
3. Write or confirm the `log/YYYY-MM-DD.md` entry (Claude drafts; you edit)

### 5. Session Quiz

After each session, take a 10-question interactive quiz: 7 multiple-choice + 2–3 short-answer. Short-answer questions can't be gamed by option length and are graded against a rubric. The quiz mixes conceptual, applied-scenario, trade-off, and "subtly wrong" question types. See `CLAUDE.md` → Session Quiz for the full rules (length normalisation, answer-distribution checks, etc.).

> "Give me the quiz for this session"

Below 7/10 means review the weak areas before advancing.

### 5b. Capstone (phase end)

A session quiz proves recall. A **capstone** proves you can apply it. Each phase in the plan file names its capstone (e.g., "a working order-book depth visualiser in C++", "a backtest notebook comparing TWAP and VWAP"). When all sessions in the phase are done, finish the capstone and commit it to `artefacts/<topic>/phase-N/`. A phase isn't closed until its capstone exists.

### 5c. Retrieval check (7 days after phase close)

When a phase closes, Claude schedules a 7-day retrieval check (`mcp__scheduled-tasks__create_scheduled_task`). At the fire time, Claude picks 3 questions from the phase's quizzes without revealing answers; you answer from memory. Results land in that day's `log/` entry. This is the one ritual that reliably moves knowledge into long-term memory.

### 6. Track Progress

Ask Claude to update `PROGRESS.md` after each session. The dashboard shows active topics, completion percentage, next session, and **Last Activity** (date of most recent session). If Last Activity slips more than a week on an active topic, that's the signal to either restart or shelve.

### 7. Complete a Topic

When all days are checked off and every phase's capstone exists:

```bash
mv topics/<topic-name>.md completed/topics/
mv plans/<topic-name>.md completed/plans/
```

Leave `artefacts/<topic>/` in place — it's the permanent record of what you built. Update `PROGRESS.md` to move the topic to the "Completed" table.

## Conventions

- **Filenames:** kebab-case, e.g., `rust-ownership.md`
- **Session length:** 2 hours per day
- **Parallel topics:** 2-3 at a time (more gets hard to sustain)
- **Log entries:** One file per day, even if you work on multiple topics
- **Dates:** YYYY-MM-DD format everywhere
