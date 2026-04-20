# Templates

Reusable rendering tools for the learning-plan repo.

## `render-slides.py`

A zero-dependency Python script that converts a markdown source file into a single-page HTML slide deck with keyboard navigation, progress dots, a light/dark theme toggle, and Mermaid diagram support.

### Usage

```
python3 docs/templates/render-slides.py <input.md> <output.html> [--title "Deck Title"]
```

### Slide source format

Slides are separated by a line containing only `---` (three dashes). The first slide's first `#` heading is used as the deck title unless `--title` is passed.

```markdown
# Phase 1 — Topic Foundations

A one-sentence hook for the deck.

---

## Concept One

- point
- point
- point

```mermaid
graph LR
  A --> B
```

---

## Concept Two

**Why it matters:** one or two paragraphs.
```

### Supported markdown

Headers (`# ## ###`), bold, italic, inline code, links, unordered lists, ordered lists, blockquotes, fenced code blocks (`\`\`\`lang`). A `\`\`\`mermaid` fence renders as a diagram at runtime via the CDN-loaded Mermaid library.

### Output

Self-contained HTML. Open via `file://` or serve from the `static-server` config in `.claude/launch.json` (http://localhost:8000).

### Tests

```
python3 -m unittest docs/templates/test_render_slides.py
```
