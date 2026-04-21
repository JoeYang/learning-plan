---
name: axiom-viz
description: Interactive visualisations built on the Axiom design system — memory layouts, binary tree traversals (DFS), line charts comparing growth strategies. Triggers on requests to "visualize X", "show me how X works step by step", "interactive diagram for X", especially when X is a CS/engineering concept like memory, trees, graphs, or data-growth curves.
user-invocable: true
---

# axiom-viz

React-based interactive figures that plug into the Axiom visual system. Built with Vite so they reload instantly during authoring and can be imported into any React host project.

## When to use this skill

Use this skill when the user wants a **dynamic** explanation of a concept — one that benefits from user input (hover, scrub, click, toggle) rather than a static slide. Typical triggers:

- "visualise X", "animate X", "step through X"
- "memory layout", "struct padding", "alignment"
- "tree traversal", "DFS", "BFS", "binary tree"
- "growth strategy", "capacity doubling", "amortized cost"

If the concept is static and textual — a trade-off table, a list of rules, a definition — use the `axiom-design` slides skill instead.

## What's in this skill

```
axiom-viz/
├── SKILL.md           ← this file
├── README.md          ← human-readable usage
├── package.json       ← vite + react + react-dom
├── vite.config.js     ← React plugin + parent-dir fs allowlist
├── index.html         ← mount point
├── main.jsx           ← imports Axiom tokens + styles, mounts <App />
├── styles.css         ← harness chrome (top bar, viz card, scrubber, narration)
├── App.jsx            ← default demo page with 3 VizCards
├── VizCard.jsx        ← figure frame with title + caption + optional foot
├── TopNav.jsx         ← minimal top nav chrome
├── Scrubber.jsx       ← reusable play/step/seek control
├── MemoryLayout.jsx   ← struct padding demo (default 24 B vs reordered 16 B)
├── TreeTraversal.jsx  ← DFS pre-order with call-stack panel
└── LineChart.jsx      ← capacity growth ×2 vs ×1.5 with hover tooltip
```

## First-time setup

```
cd .claude/skills/axiom-viz
npm install
npm run dev
```

Opens http://localhost:5173. Design tokens load from the sibling `axiom-design` skill via a relative CSS import.

## Adding a new visualisation

1. Create `<Concept>.jsx` as a React default-exported component. Import `Scrubber` if you need play/step controls.
2. Add an import + `<VizCard>` wrapper in `App.jsx` (or build your own page).
3. Use CSS variables from Axiom (`var(--accent-500)`, `var(--fg-1)`, `var(--bg-raised)`, etc.) — never raw hex.
4. Keep the one-highlight-per-figure rule: accent blue draws the eye to the single idea the viz teaches.

## Copying a component into another project

The JSX files use only standard React + Axiom CSS variables. Copy `<Component>.jsx` + `Scrubber.jsx` (if used) + the relevant class styles from `styles.css` into any React host. Ensure Axiom's `colors_and_type.css` is imported at root.

## Conventions

From Axiom (see `.claude/skills/axiom-design/AXIOM_README.md`):
- Sentence case, em-dashes, Unicode math — never emoji.
- 120/200/320ms transitions with `var(--ease-out)`. No bouncy easing.
- Flat cards with hairline borders. No drop shadows.
- Serif for display, sans for body, mono for code + data labels.
