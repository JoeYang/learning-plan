# axiom-viz

Interactive React visualisations for the Axiom design system.

## Quick start

```
cd .claude/skills/axiom-viz
npm install
npm run dev
```

Opens http://localhost:5173 with three demo figures: memory layout padding, DFS on a binary tree, and capacity-growth comparison.

The dev server is also registered in `.claude/launch.json` as `viz-harness` — use your editor's run command if you prefer.

## Why a separate skill

Slides (`axiom-design`) are the default pre-read. Some concepts genuinely need motion or user input to click — memory grids with padding, trees with an animated call stack, line charts with hover tooltips. Those go here as React components so the reader can drive the figure themselves.

## Dependencies

Inside this directory only:

- `react`, `react-dom` (18.x)
- `vite`, `@vitejs/plugin-react` (5.x / 4.x)

The rest of the repo stays dependency-free. `node_modules/` and `package-lock.json` under this dir are gitignored.

## File map

See `SKILL.md` for the full index. TL;DR:
- `App.jsx` — demo page that composes `VizCard` + 3 viz components
- `VizCard.jsx`, `TopNav.jsx`, `Scrubber.jsx` — reusable chrome
- `MemoryLayout.jsx`, `TreeTraversal.jsx`, `LineChart.jsx` — concept-specific figures

## Notes

- All components use Axiom CSS variables from `../axiom-design/colors_and_type.css`, imported by `main.jsx`.
- To copy a component into another React project, you need the component file + `Scrubber.jsx` (if used) + the matching class rules from `styles.css` + Axiom's design tokens at the host project's root.
