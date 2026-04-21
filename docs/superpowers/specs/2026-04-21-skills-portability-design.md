# Skills portability — design spec

**Date:** 2026-04-21
**Status:** awaiting approval

## Goal

Make the learning-structure toolkit (design assets, slide renderer, workflow) travel with the repo as project-scoped Claude skills, so a `git clone` on any machine brings everything along — no separate install step beyond `npm install` inside one skill directory.

## Structure

```
.claude/skills/
├── axiom-design/            ← design tokens + slide renderer
│   ├── SKILL.md
│   ├── colors_and_type.css
│   ├── deck-stage.js
│   ├── render-slides.py
│   ├── test_render_slides.py
│   ├── assets/{logo.svg, logo-mark.svg}
│   └── README.md
├── axiom-viz/               ← React viz components + Vite harness
│   ├── SKILL.md
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── main.jsx
│   ├── {App,VizCard,Scrubber,MemoryLayout,TreeTraversal,LineChart,TopNav}.jsx
│   └── README.md
├── learning-session/        ← Pre-read → Apply → Prove workflow
│   └── SKILL.md
└── interactive-visual/      ← vendored from ~/.claude/skills/
    └── SKILL.md
```

## Skill responsibilities

| Skill | Triggers | Produces |
|---|---|---|
| `axiom-design` | "slides", "deck", "design system", "generate phase deck" | HTML decks via `render-slides.py`; styled HTML using tokens |
| `axiom-viz` | "visualize X", "memory layout", "tree traversal", "chart" | React viz component; harness preview via `npm run dev` |
| `learning-session` | "start session N", "run session", "quiz me on X" | End-to-end session: deck → checkboxes → quiz → capstone → log → retrieval schedule |
| `interactive-visual` | "interactive explainer", "animated diagram" | Single-file HTML explainer for `docs/interactive/<topic>/` |

## Resolved design decisions

| Decision | Choice | Why |
|---|---|---|
| Distribution | Project-scoped `.claude/skills/` | Travels with clone. No global install step. User preference. |
| Viz stack | React + Vite harness in skill dir | Interactive diagrams work out of the box; node_modules gitignored, isolated from repo root. |
| Workflow packaging | One `learning-session` skill orchestrates full flow | Matches Joe's preference for one-invocation runs, not three-step friction. |
| Node deps location | Inside `.claude/skills/axiom-viz/` only | Rest of repo stays Python-stdlib-only. First-clone cost = one `npm install` in one dir. |
| Renderer path | `git mv` to new location, update 3 call sites | Keeps the renderer with its design system. No shim. Clean. |
| Renderer asset paths | `/docs/templates/axiom/` → `/.claude/skills/axiom-design/` | Two lines in the HTML shell; tests' one path assertion. |

## Files moved (via `git mv` to preserve history)

```
docs/templates/axiom/                  → .claude/skills/axiom-design/
docs/templates/render-slides.py         → .claude/skills/axiom-design/
docs/templates/test_render_slides.py    → .claude/skills/axiom-design/
docs/templates/README.md                → .claude/skills/axiom-design/ (renamed README.md)
```

After the move, `docs/templates/` disappears entirely.

## Call sites to update

- `CLAUDE.md` — Structure section and the `render-slides.py` command example in the Pre-read workflow.
- `docs/slides/README.md` — example command line.
- `.claude/skills/axiom-design/AXIOM_README.md` — path refs to sibling files.
- `docs/slides/claude-certified-architect/phase-1.html` — regenerate (absolute asset URLs change).

## New dev server

`.claude/launch.json` gains a `viz-harness` entry:

```json
{
  "name": "viz-harness",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["--prefix", ".claude/skills/axiom-viz", "run", "dev"],
  "port": 5173
}
```

## Commit plan (each under 400 LOC per CLAUDE.md)

1. **refactor(skills)**: move Axiom + renderer into `.claude/skills/axiom-design/` via `git mv`; update the 2 asset paths in `render-slides.py`, the 1 path assertion in tests, 3 call-site examples in docs; re-render Phase 1 deck. Expected diff: ~30 real lines + renames.
2. **feat(skills)**: add `axiom-viz` skill — copy React JSX from `/tmp/axiom/ui_kits/visualizations/`, add `package.json`, `vite.config.js`, `index.html`, `main.jsx`, `SKILL.md`. Register dev server in `launch.json`. Gitignore `node_modules/` under the skill. ~150 LOC plus viz file copies.
3. **feat(skills)**: add `learning-session` skill — extract Pre-read → Apply → Prove into a reusable `SKILL.md` with invocation patterns, preconditions (project must have plans/, topics/, quizzes/, artefacts/, docs/slides/ dirs), and step-by-step flow. ~120 LOC of prose.
4. **feat(skills)**: copy `interactive-visual` skill from `~/.claude/skills/` into the project so it clones with the repo.
5. **docs**: update `README.md` + `CLAUDE.md` to document the `.claude/skills/` layout and the one-time `npm install` step. ~40 LOC.

## Non-goals

- Not publishing the skills to a public marketplace.
- Not creating a separate `learning-toolkit` repo — user explicitly wanted project-scoped.
- Not adding syntax highlighting to slides in this change — scope creep.
- Not adding MathJax / KaTeX — scope creep.

## Verification

Each commit ends in a working state. After the final commit:

1. `python3 -m unittest .claude/skills/axiom-design/test_render_slides.py` — all 24 pass.
2. Re-render Phase 1 deck using the new path, serve on :8000, confirm HTTP 200 + visual parity with the pre-move version.
3. `cd .claude/skills/axiom-viz && npm install && npm run dev` — harness loads on :5173, renders the Axiom visualization demo.
4. `ls .claude/skills/` — exactly four directories: `axiom-design`, `axiom-viz`, `learning-session`, `interactive-visual`.
5. `docs/templates/` is gone.
