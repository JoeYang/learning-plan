# Bootstrap a learning-plan repo from this document

A single-file genesis guide for the personal-learning-tracker project in this repo. Following this document end to end produces a working clone — same structure, same conventions, same skills — in a fresh directory. The content (your topics, plans, quizzes, session logs) starts empty; everything else is reproducible.

Use this when:
- You want to start a new learning-plan for a different subject (e.g. you did this for `sophie-learning-plan` manually — this file makes it 15 minutes instead of an afternoon)
- You want to hand the skeleton to someone else
- You want to back up the architectural decisions in one reviewable artefact, independent of the code

## 0. Philosophy in one paragraph

A personal learning tracker built on three rituals per session — **Pre-read, Apply, Prove** — with a phase-closing **Capstone** gate and a **7-day retrieval check** that runs itself. Content is plain markdown. A stdlib-only Python renderer turns per-phase markdown into self-contained HTML slide decks (no server, no build step). Sessions are orchestrated by a Claude skill so the three rituals happen every time; that skill enforces a quiz-audit rule set that prevents gaming by option length or position. Branching/commit hygiene is captured in rules so progress is legible in git history.

The point is evidence-of-mastery, not progress-on-a-syllabus.

## 1. Directory skeleton

Create this layout. Everything below expects it.

```bash
mkdir -p \
  topics plans log completed \
  quizzes artefacts \
  docs/slides docs/interactive \
  .claude/skills/learning-session \
  .claude/skills/axiom-design \
  .claude/skills/axiom-viz \
  .claude/skills/interactive-visual
```

Final tree:

```
<repo>/
├── BOOTSTRAP.md              ← this file
├── README.md                 ← project-level intro (template below)
├── CLAUDE.md                 ← conventions + workflow for Claude (template below)
├── PROGRESS.md               ← dashboard (template below)
├── topics/
│   ├── _template.md          ← template below, copy for each topic
│   └── <topic-name>.md       ← one per subject
├── plans/
│   └── <topic-name>.md       ← day-by-day plan for each topic
├── log/
│   └── YYYY-MM-DD.md         ← per-day 3–5 line session reflections
├── quizzes/
│   └── <topic>/
│       └── phase-N/
│           └── session-NN.md ← one file per session quiz
├── artefacts/
│   └── <topic>/
│       └── phase-N/          ← capstone deliverables per phase
├── docs/
│   ├── slides/<topic>/       ← phase-N.md → phase-N.html (rendered)
│   └── interactive/<topic>/  ← one-off HTML explainers
├── completed/
│   ├── topics/               ← archived on completion
│   └── plans/
└── .claude/
    ├── launch.json           ← dev-server config (viz-harness only)
    └── skills/               ← project-scoped Claude skills
        ├── learning-session/ ← session orchestrator (SKILL.md only, inlined below)
        ├── axiom-design/     ← design tokens + slide renderer (fetch from upstream)
        ├── axiom-viz/        ← React+Vite interactive visualisations (fetch from upstream)
        └── interactive-visual/ ← pattern-driven HTML explainer generator (fetch from upstream)
```

## 2. Conventions

| Topic | Rule |
|---|---|
| Filenames | kebab-case: `cpp-trading-systems.md`, not `cppTradingSystems.md` |
| Dates | `YYYY-MM-DD` everywhere |
| Plan checkboxes | `- [ ]` pending, `- [x]` done |
| One deck per phase | Not per session. Decks summarise the phase's key concepts in 5–10 slides. |
| One capstone per phase | Not per session. Listed in the plan's `Capstone:` line for the phase. |
| Feature-branch commits | Never commit to `main` directly. One feature branch per logical change. |
| Conventional Commits | `feat(scope):`, `docs(scope):`, `fix(scope):`, `refactor(scope):` |
| Commit size | Target ≤ 200 lines / hard max 400 lines of code (docs excluded). Split bigger changes. |
| Session advance branch | `feat/progress-<topic>-session-<N>` |

## 3. Workflow — Pre-read → Apply → Prove

Every session runs through the same three steps in order. Skipping Pre-read is the most common way sessions turn into box-ticking.

### 3.1 Pre-read (10–15 min)

1. Identify the first unchecked `- [ ]` session header in `plans/<topic>.md`. That's your current session.
2. Determine its phase.
3. Check for `docs/slides/<topic>/phase-N.md`.
   - **If present** — render it:
     ```bash
     python3 .claude/skills/axiom-design/render-slides.py \
       docs/slides/<topic>/phase-N.md \
       docs/slides/<topic>/phase-N.html \
       --eyebrow "<topic> · phase N"
     ```
     Open the HTML directly — `file://` works, the renderer inlines CSS and JS so the output is self-contained.
   - **If missing** — generate the markdown source first. Decks follow the **deck authoring rules** below.

### 3.2 Apply

Walk the session's checkboxed exercises one at a time. For each `- [ ]`:
1. Explain the concept.
2. Ask the learner to respond or apply it.
3. Flip to `- [x]` only once they actually demonstrate understanding.

If a concept is genuinely dynamic (memory layout, tree traversal, animated flow), spin up the `axiom-viz` skill. For static-but-visual concepts, prefer a slide.

Keep a running list of anything the learner got wrong on first pass — these feed the quiz.

### 3.3 Prove — the 10-question interactive quiz

Use the `AskUserQuestion` tool (Claude Code) to present the quiz one question at a time.

**Composition:**
- 7 multiple-choice + 2–3 short-answer.
- Mix: conceptual, applied-scenario, trade-off ("given these constraints, which approach wins?"), and at least one **"subtly wrong"** question (three options look right; one has a small error).
- Scenarios with constraints. Distractors all "work" — only one is **"best given constraints"**.

**Self-audit BEFORE showing the quiz — not after:**

1. **Length normalisation** — all four options within ±20% character count of each other. If the correct answer is longer, pad the distractors with plausible specifics; don't trim the correct answer to something evasive.
2. **Correct-answer distribution** — across the quiz, correct position should be roughly uniform across A/B/C/D. No position is correct for more than ~35% of questions.
3. **Longest-option check** — correct answer is the longest option in ≤ ~30% of questions.
4. **No giveaway phrasing** — strip "always", "never", "all of the above" from distractors unless genuinely correct.

If any audit fails, regenerate the offending questions.

**Grading:**
- Immediate feedback per answer with a one-line explanation.
- Short-answer: show rubric, mark which points were hit, give full / half / none credit.
- Final score + weak areas.
- Below 7/10: suggest reviewing missed topics before the next session.

### 3.4 Capstone (only when this session closes a phase)

The quiz proves recall and reasoning. The **capstone** proves application. A phase isn't closed until its capstone artefact exists at `artefacts/<topic>/phase-N/`.

Examples: a working `.cpp` demonstrating the phase's concepts, a backtest notebook with a written trade-off reflection, a scenario design doc a peer could review, a scored mock exam.

### 3.5 7-day retrieval check (only when this session closes a phase)

Schedule it — don't rely on good intentions.

```
mcp__scheduled-tasks__create_scheduled_task(
  taskId   = "retrieval-check-<topic>-phase-<N>",
  fireAt   = 7 days from today at 09:00 local,
  prompt   = "Run a 3-question retrieval check for <topic> Phase <N>.
              Pick 3 questions from quizzes/<topic>/phase-<N>/ without
              revealing answers. Ask learner to answer from memory.
              Grade. Log the result to log/<today>.md."
)
```

### 3.6 Session log (Claude drafts, learner edits)

At session end, draft 3–5 lines in `log/YYYY-MM-DD.md`:

```markdown
## YYYY-MM-DD — <Topic> Session <N> (<Session title>)

- **Learned:** the one thing that actually clicked.
- **Blocked:** the one thing that didn't click (or empty).
- **Next:** the focus for the next session.

Quiz score: N/10. [notes on weak areas]
```

Show the draft for confirmation before writing to disk. Low-friction reflection; not a journal.

### 3.7 Mark done and advance

Only after all six steps above:

- Tick the session's `- [ ]` → `- [x]` in `plans/<topic>.md`.
- Update `PROGRESS.md`: increment Days Done, bump percentage, advance Next Session, set Last Activity to today.
- Commit on `feat/progress-<topic>-session-<N>`.

## 4. Deck authoring rules — non-negotiable

When writing a phase deck (`docs/slides/<topic>/phase-N.md`), follow these every time. They exist because jumping straight to math leaves formulas feeling arbitrary and Greek notation you can't pronounce blocks rehearsal.

### 4.1 Pedagogical structure — Problem → Challenge → Solution → Validation

Every technique, algorithm, or model introduced must be framed in this order:

- **Problem** — what real-world goal are we trying to achieve? Plain English, no math.
- **Challenge** — what makes it hard? What can go wrong? Name the failure modes the technique defends against.
- **Solution** — the mechanism first, then the math. Show how each term in a formula maps back to a specific challenge.
- **Validation** — how do you verify it's working? Metrics, backtests, sanity checks.

Lead every deck with a "Problem" slide before any notation.

### 4.2 Greek symbol gloss — always pronounce and define

Before the first slide containing Greek letters, add a cheat-sheet slide listing every Greek symbol used in the deck with:

- Its English pronunciation (*gamma*, *sigma*, *kappa*, *delta*, *lambda*, *mu*, *theta*, *beta*, *alpha*, *rho*, *epsilon*, *pi*, *Sigma*, *Delta*, *omega*, *phi*, *chi*, *psi*).
- Its **contextual** meaning in this deck (σ = volatility here, not standard deviation in general).
- A "read aloud" example for the headline formula.

Use the common English reading, not Modern Greek.

### 4.3 Formatting

- Sentence case, em-dashes, Unicode math: `→ ≤ ≥ ≠ ∑ ∞ π θ σ γ κ λ ᵢ ₜ ²` etc.
- No emoji.
- Formulas go in fenced code blocks. The renderer has **no LaTeX/KaTeX support** — `$$...$$` will render as literal text.

## 5. The skills

Four `.claude/skills/` entries travel with the repo. Two are documents (inline below); two are code (fetch from upstream).

### 5.1 learning-session — inline

Create `.claude/skills/learning-session/SKILL.md` with this exact content:

```markdown
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
(see §1 of BOOTSTRAP.md)

## Required companion skills

- `axiom-design` — for `render-slides.py`; used in Pre-read.
- `axiom-viz` — when a concept needs interactive motion rather than a slide.
- `interactive-visual` — for single-file HTML explainer pages saved to `docs/interactive/<topic>/`.

## The flow

(matches §3 of BOOTSTRAP.md — Pre-read → Apply → Prove → Capstone → 7-day retrieval → Log → Mark done)

## Anti-patterns to avoid

- **Skipping Pre-read** when the deck is missing — the whole point is the deck gets generated on demand, not later.
- **Marking a session done without the quiz** — box-ticking returns.
- **Marking a phase-closing session done without the capstone** — evidence layer collapses.
- **Hand-authoring the quiz without the self-audit** — length-based gaming creeps back in.
- **Inventing retrieval-check cadence manually** — use scheduled-tasks or it won't happen.

## What to do if the user just says "quiz me"

Skip Pre-read and Apply. Ask which topic + phase + session range. Run the Prove step only. Do NOT create a log entry or mark anything done.
```

That's the complete skill — 148 lines in the source repo, distilled to the parts that matter here. The flow is already covered by §3 of this document; no need to repeat it verbatim.

### 5.2 axiom-design — fetch from upstream

Design system + stdlib Python slide renderer. Too much code to inline cleanly (~1,400 lines across four files). Fetch these from the source repo:

```
.claude/skills/axiom-design/
├── SKILL.md                    ← skill manifest (~40 lines — inlined below)
├── README.md                   ← design-system overview
├── AXIOM_README.md             ← full design spec (colors, type, voice)
├── colors_and_type.css         ← CSS variables (fonts, palette, spacing)
├── deck-stage.js               ← <deck-stage> web component (~600 lines)
├── render-slides.py            ← markdown → HTML renderer (~450 lines, stdlib only)
├── test_render_slides.py       ← 24-case unittest suite
└── assets/
    ├── logo.svg
    └── logo-mark.svg
```

**How to fetch:**

```bash
git clone https://github.com/JoeYang/learning-plan.git /tmp/lp-upstream
cp -r /tmp/lp-upstream/.claude/skills/axiom-design/. .claude/skills/axiom-design/
rm -rf /tmp/lp-upstream
```

Or, if you're starting from an existing clone of the upstream and just emptying content:

```bash
# Delete learner content, keep scaffolding + skills
rm -rf topics/*.md plans/*.md log/*.md quizzes/* artefacts/* \
       docs/slides/* docs/interactive/* completed/*
# Keep topics/_template.md
git checkout -- topics/_template.md PROGRESS.md
```

**The SKILL.md content:**

```markdown
---
name: axiom-design
description: Use this skill to generate well-branded interfaces and assets for Axiom — a minimalist, academic design system for interactive self-study learning materials (slides, interactive charts, memory diagrams, tree traversals) in science, CS, and engineering.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

## Quick orientation

- Tokens live in `colors_and_type.css` (CSS variables for color, type, spacing, radii, shadows, motion).
- Slides — 1920×1080, uses `<deck-stage>` web component. Title / section / concept+figure / bullets / chart / quote / dark-summary templates.
- Icons — Lucide via CDN.
- Logo — `assets/logo.svg` + `assets/logo-mark.svg`.

## Non-negotiables

- Sentence case. Em-dashes. Unicode math. No emoji.
- One highlight per figure. Accent is indigo `#3b4cad`, used sparingly.
- Flat cards with hairline borders — never drop-shadow.
- No gradients. No bouncy easing. 120–320ms animation durations.
- Serif for display and definitions; sans for body and UI; mono for code.

## Renderer constraints (`render-slides.py`)

- No LaTeX / KaTeX / MathJax support. `$$...$$` renders as literal text. Use Unicode math in fenced code blocks.
- Slides separated by a line containing only `---`. First slide becomes the title slide.
- CSS and JS are inlined at render time; output is self-contained, works via file://.

## Pedagogical rules for learning decks

Follow the deck authoring rules in BOOTSTRAP.md §4 — Problem → Challenge → Solution → Validation, Greek symbol cheat-sheet, Unicode formatting. Non-negotiable.
```

**Rendering a deck:**

```bash
python3 .claude/skills/axiom-design/render-slides.py \
  docs/slides/<topic>/phase-N.md \
  docs/slides/<topic>/phase-N.html \
  --eyebrow "<topic> · phase N"
```

Open the output directly — no server.

### 5.3 axiom-viz — fetch from upstream

React + Vite interactive visualisations. Substantial (Node deps, React components). Fetch and run:

```bash
cp -r /tmp/lp-upstream/.claude/skills/axiom-viz/. .claude/skills/axiom-viz/
cd .claude/skills/axiom-viz
npm install
npm run dev    # http://localhost:5173
```

Components shipped: `VizCard`, `Scrubber`, `MemoryLayout`, `TreeTraversal`, `LineChart`.

Use when a concept is dynamic enough that a slide doesn't cut it — animated traversals, parameter tuning, memory layouts that change.

### 5.4 interactive-visual — fetch from upstream

Pattern-driven one-off HTML explainer generator. Medium-sized SKILL.md (~290 lines). Fetch or skip.

**When to use:** user asks "visualize X", "show me how X works", "create a diagram of X", or any request where an interactive browser-based visual would aid understanding.

**Pattern library** (signal words the skill matches on):

| Pattern | Best for |
|---|---|
| step-stepper | Sequential processes, protocols |
| packet-simulation | Network protocols, message exchanges |
| sandbox | Tunable systems, parameter exploration |
| annotated-architecture | System design, component relationships |
| side-by-side | Trade-off comparisons |
| state-machine | Object lifecycles, FSMs |
| sequence-diagram | Method calls, service interactions |
| data-structure-explorer | Trees, graphs, hash tables |
| timeline | Concurrent processes, race conditions |
| flowchart | Decision logic, debugging, routing |

**Output:** self-contained HTML with React 18 via CDN + Babel standalone + inline SVG + CSS animations. Dev server on port 3456 during iteration; saved to `docs/interactive/<topic>/<concept>.html` when confirmed.

Fetch from upstream if needed. Otherwise you can skip this skill until a specific concept calls for it.

## 6. Template files — inline and ready to copy

### 6.1 `topics/_template.md`

```markdown
# Topic: [Name]

## Why I Want to Learn This
<!-- What motivated you? What will you use it for? -->

## Current Knowledge Level
<!-- none / beginner / intermediate -->

## Goal
<!-- What does "done" look like? Be specific. -->

## Capstone: what artefact proves mastery?
<!-- Not "I read the material" — a thing that can be shown to a peer.
     Examples: a working C++ program, a backtest notebook with written
     trade-off analysis, a mini design doc a peer could review, a
     scored mock exam. One capstone per phase; list phase capstones
     in the generated plan. -->

## Resources (optional)
<!-- Books, courses, docs, repos you already know about -->

## Time Estimate
<!-- How many days/weeks do you think this will take? -->

## Priority
<!-- high / medium / low -->
```

### 6.2 `plans/<topic>.md` — structure of a real plan

```markdown
# Learning Plan: <Topic Name>

**Start date:** YYYY-MM-DD
**Target completion:** ~YYYY-MM-DD (~N weeks)
**Schedule:** N sessions/week, ~M min each
**Status:** in-progress

> Approach: one-line framing of how this plan differs from a generic syllabus.

---

## Capstones by Phase

A phase isn't closed until its capstone artefact exists under `artefacts/<topic>/phase-N/`.

| Phase | Capstone |
|---|---|
| Phase 1 (<Name>) | `artefacts/.../phase-1/<file>.md` — one-line description |
| Phase 2 (<Name>) | `artefacts/.../phase-2/<file>.md` — one-line description |
| ...             |                                                         |

---

## Phase 1: <Phase Name> (Sessions 1–N)

<Optional prose describing what this phase achieves.>

**Phase 1 capstone:** `artefacts/<topic>/phase-1/<file>.md`

**Visual:** `docs/slides/<topic>/phase-1.md` — 5–10 slides covering the phase themes.

### Session 1: <Session title>
**Objective:** <single-sentence concrete objective>
- [ ] <concrete thing to learn/apply>
- [ ] <another>
- [ ] Notes: <what to capture>
**Key concepts:** <comma-separated>
**Resources:** <book chapter, paper, blog — be specific>

### Session 2: ...
```

### 6.3 `PROGRESS.md` — starter

```markdown
# Learning Progress Dashboard

*Last updated: YYYY-MM-DD*

> **Last Activity** = date of the most recent session commit for that plan
> (from `git log -1 --format=%cs -- plans/<topic>.md`). If it slips more
> than 7 days on an active topic, surface it in the Weekly Summary and
> decide: restart, reshape, or shelve.

## Active Topics

| Topic | Started | Days Done | Days Total | Progress | Schedule | Next Session | Last Activity |
|-------|---------|-----------|------------|----------|----------|--------------|---------------|

## Shelved Topics

| Topic | Shelved | Notes |
|-------|---------|-------|

## Completed Topics

| Topic | Started | Completed | Days Spent |
|-------|---------|-----------|------------|

## Weekly Summary
<!-- Updated weekly — what went well, what was hard, adjustments -->
```

### 6.4 `CLAUDE.md` — starter (the essentials)

```markdown
# CLAUDE.md

Guidance for Claude Code when working with this repository.

## What this repo is

Personal learning tracker. Markdown content; stdlib Python renderer for slide decks; project-scoped Claude skills at `.claude/skills/`.

## Structure

- `topics/` — topic definitions
- `plans/` — day-by-day learning plans
- `log/` — session reflections (YYYY-MM-DD.md)
- `quizzes/<topic>/` — per-session quizzes and results
- `artefacts/<topic>/phase-N/` — capstone deliverables
- `docs/slides/<topic>/` — per-phase slide markdown (rendered to HTML)
- `docs/interactive/<topic>/` — interactive explainer pages
- `.claude/skills/` — project-scoped Claude skills
- `completed/` — archive
- `PROGRESS.md` — central dashboard

## Conventions

- Filenames: kebab-case
- Dates: YYYY-MM-DD
- Plan checkboxes: `- [ ]` pending, `- [x]` done

## Workflow

Every session runs Pre-read → Apply → Prove. See BOOTSTRAP.md §3 for the full flow.
Session quizzes follow the audit rules in BOOTSTRAP.md §3.3.
Deck authoring follows the rules in BOOTSTRAP.md §4.

## Branching

- Never commit to main directly
- Feature branch per logical change: `feat/progress-<topic>-session-<N>` for session advances
- Conventional Commits: `feat(scope):`, `docs(scope):`, `fix(scope):`, `refactor(scope):`
- Target ≤ 200 lines / hard max 400 lines per commit (docs excluded)
```

### 6.5 `README.md` — starter

```markdown
# <Your Name>'s Learning Plan

Personal learning tracker built on Pre-read → Apply → Prove rituals with per-phase capstones.

See **BOOTSTRAP.md** for the full project architecture, conventions, and how to bootstrap a fresh copy.

## Active topics

See `PROGRESS.md`.

## Getting started

No install needed for slides — the renderer is stdlib Python and outputs self-contained HTML:

\`\`\`bash
python3 .claude/skills/axiom-design/render-slides.py \
  docs/slides/<topic>/phase-N.md \
  docs/slides/<topic>/phase-N.html
xdg-open docs/slides/<topic>/phase-N.html    # or double-click
\`\`\`

Interactive visualisations need a one-time install:

\`\`\`bash
cd .claude/skills/axiom-viz
npm install
npm run dev    # http://localhost:5173
\`\`\`
```

### 6.6 `.claude/launch.json`

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "viz-harness",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["--prefix", ".claude/skills/axiom-viz", "run", "dev"],
      "port": 5173
    }
  ]
}
```

### 6.7 `.gitignore`

```
.claude/settings.local.json
__pycache__/
*.pyc

# Generated slide deck HTML — rebuilt from the .md via render-slides.py
docs/slides/**/*.html

# Playwright MCP scratch output
.playwright-mcp/

# axiom-viz Node deps — installed via `npm install` inside the skill dir
.claude/skills/axiom-viz/node_modules/
.claude/skills/axiom-viz/package-lock.json
.claude/skills/axiom-viz/dist/
```

### 6.8 Sample `log/YYYY-MM-DD.md` entry

```markdown
## 2026-04-21 — Trading Algos Session 5 (Avellaneda-Stoikov)

- **Learned:** Market making is renting out balance sheet for a spread, not forecasting direction. The two-term optimal spread literally prices inventory risk and adverse selection as separate compensations — each term has a business reason.
- **Blocked:** The HJB derivation math itself (skipped the full step-by-step; derivation writeup deferred).
- **Next:** Session 6 — inventory management and skewing in practice (GLFT extensions, what the textbook misses).

Quiz score: 8.5 / 10 (above the 7/10 bar). Miss on Q7 (calibration method match) and half-credit on Q9.
```

## 7. Bootstrap recipe — concrete steps from empty dir

```bash
# 1. Create the repo
mkdir my-learning-plan && cd my-learning-plan
git init -b main

# 2. Build the scaffold (§1)
mkdir -p \
  topics plans log completed \
  quizzes artefacts \
  docs/slides docs/interactive \
  .claude/skills/learning-session \
  .claude/skills/axiom-design \
  .claude/skills/axiom-viz \
  .claude/skills/interactive-visual

# 3. Drop in the template files (copy from §6 of this doc)
#    - topics/_template.md
#    - PROGRESS.md
#    - CLAUDE.md
#    - README.md
#    - .claude/launch.json
#    - .gitignore
#    - .claude/skills/learning-session/SKILL.md

# 4. Fetch the code skills from upstream
git clone https://github.com/JoeYang/learning-plan.git /tmp/lp-upstream
cp -r /tmp/lp-upstream/.claude/skills/axiom-design/. .claude/skills/axiom-design/
cp -r /tmp/lp-upstream/.claude/skills/axiom-viz/. .claude/skills/axiom-viz/
cp -r /tmp/lp-upstream/.claude/skills/interactive-visual/. .claude/skills/interactive-visual/
rm -rf /tmp/lp-upstream

# 5. Copy BOOTSTRAP.md for future re-bootstraps
cp /path/to/BOOTSTRAP.md ./

# 6. First commit
git add .
git commit -m "chore: initial scaffold from BOOTSTRAP.md"

# 7. Create your first topic
cp topics/_template.md topics/<first-topic>.md
# Fill it in, then ask Claude Code to generate a plan:
#   > "Read topics/<first-topic>.md and generate a day-by-day plan in plans/"

# 8. Run your first session
#   > "Start session 1 of <first-topic>"
# The learning-session skill takes over from there.
```

## 8. What you should NOT reproduce from upstream

- Any `topics/*.md`, `plans/*.md`, `log/*.md`, `quizzes/*`, `artefacts/*`, `completed/*`, `docs/slides/*.md`, `docs/interactive/*`
- Any `.claude/settings.local.json` or user-specific harness config
- Any backlog entries that were specific to the upstream user's journey
- Git history from the upstream repo (fresh `git init` gives you a clean audit log)

## 9. Sanity check after bootstrap

```bash
# Renderer works?
python3 -m unittest .claude/skills/axiom-design/test_render_slides.py
# → 24 tests pass

# Skill files present?
ls .claude/skills/*/SKILL.md
# → four lines

# Scaffold complete?
ls topics/_template.md PROGRESS.md CLAUDE.md README.md BOOTSTRAP.md .gitignore
# → no "No such file" errors

# Renderer produces self-contained output?
echo -e "# Test\n\nHello" > /tmp/t.md
python3 .claude/skills/axiom-design/render-slides.py /tmp/t.md /tmp/t.html
grep -c "/.claude/skills" /tmp/t.html
# → 0 (no absolute-path references; CSS + JS inlined)
```

All four commands clean → bootstrap is valid. Start your first topic.

## 10. When to update this document

- A non-negotiable rule changes (deck authoring, quiz audits, branching).
- A skill gets renamed or replaced.
- A template file gets a new required field.
- A workflow step gets added or removed.

Treat this as living documentation — re-bootstrapping from a stale BOOTSTRAP.md is strictly worse than from an up-to-date one.
