---
name: axiom-design
description: Use this skill to generate well-branded interfaces and assets for Axiom — a minimalist, academic design system for interactive self-study learning materials (slides, interactive charts, memory diagrams, tree traversals) in science, CS, and engineering. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Quick orientation

- **Tokens** live in `colors_and_type.css` (CSS variables for color, type, spacing, radii, shadows, motion). Import it and wrap your root in `.axiom`.
- **Slides** — see `ui_kits/slides/`. 1920×1080, uses `<deck-stage>` web component. Title / section / concept+figure / bullets / chart / quote / dark-summary templates.
- **Visualizations** — see `ui_kits/visualizations/`. React components: `VizCard`, `Scrubber`, `MemoryLayout`, `TreeTraversal`, `LineChart`.
- **Icons** — Lucide via CDN. 1.5px stroke, `currentColor`. See `assets/icons.md`.
- **Logo** — `assets/logo.svg` (wordmark), `assets/logo-mark.svg` (mark only).

## Non-negotiables

- Sentence case. Em-dashes. Unicode math. No emoji.
- One highlight per figure. Accent is indigo `#3b4cad`, used sparingly.
- Flat cards with hairline borders — never drop-shadow "floating" cards.
- No gradients. No bouncy easing. 120–320ms animation durations.
- Serif for display and definitions; sans for body and UI; mono for code.

## Renderer constraints (`render-slides.py`)

- **No LaTeX / KaTeX / MathJax support.** `$$...$$` renders as literal text. Use fenced code blocks with Unicode math (σ² γ κ δ · → ≤ ≥ ≠ ᵢ ₜ etc.) for formulas.
- Slides separated by a line containing only `---`. First slide becomes the title slide.

## Pedagogical rules for learning decks

When authoring learning-plan decks (`docs/slides/<topic>/phase-N.md`), follow the rules in `.claude/skills/learning-session/SKILL.md` §1 (Pre-read → Deck authoring rules):

- **Problem → Challenge → Solution → Validation** for every technique introduced.
- **Greek symbol cheat-sheet slide** with pronunciation + contextual meaning before the first formula.

These are durable preferences captured from Joe's feedback; don't skip them even if the user just asks to "make slides."
