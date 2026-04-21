# axiom-design skill

The Axiom design system — minimalist academic typography and component library for self-study learning materials — plus a stdlib-only Python renderer that converts markdown into Axiom-styled HTML slide decks.

See `SKILL.md` for how Claude invokes this skill. See `AXIOM_README.md` for the full design-system spec (colors, type, voice, component rules).

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | Claude-invokable skill entry point |
| `README.md` | This file |
| `AXIOM_README.md` | Full Axiom design-system documentation |
| `colors_and_type.css` | Design tokens — CSS variables for color, type, spacing, radii, shadows, motion |
| `deck-stage.js` | `<deck-stage>` web component: 1920×1080 auto-scaled canvas, keyboard nav, localStorage, print-to-PDF |
| `render-slides.py` | Markdown → Axiom HTML deck renderer (stdlib only) |
| `test_render_slides.py` | 24 unittest cases covering the renderer |
| `assets/logo.svg` | Axiom wordmark |
| `assets/logo-mark.svg` | Axiom glyph mark |

## Rendering a deck

```
python3 .claude/skills/axiom-design/render-slides.py \
  docs/slides/<topic>/phase-N.md \
  docs/slides/<topic>/phase-N.html \
  --eyebrow "<topic> · phase N"
```

Serve it from the `static-server` config in `.claude/launch.json`:

```
http://localhost:8000/docs/slides/<topic>/phase-N.html
```

File-URL access (`file://`) does NOT work — the deck references `/.claude/skills/axiom-design/colors_and_type.css` and `/.claude/skills/axiom-design/deck-stage.js` at absolute paths, so the repo root must be the web root.

## Slide source format

Slides are separated by a line containing only `---`. The first slide's first `#` heading is used as the deck title unless `--title` is passed. The first slide automatically gets `class="slide is-title"` — serif display title, italic lead paragraph.

Override the class per slide with an HTML comment directive on the first line:

```markdown
<!-- class: is-dark -->

# Summary

...
```

Supported directives: `is-dark`, `is-section`, `is-quote`.

## Supported markdown subset

Headers (`# ## ###`), bold, italic, inline code, links, ordered/unordered lists, blockquotes, pipe tables, fenced code blocks (`\`\`\`lang`). A `\`\`\`mermaid` fence renders via the CDN-loaded Mermaid library (wrapped in Axiom's `.fig` frame).

## Tests

```
cd .claude/skills/axiom-design
python3 -m unittest test_render_slides
```

24 tests, ~40ms, stdlib only.
