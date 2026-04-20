# Slide decks

One markdown source file per **phase** at `docs/slides/<topic>/phase-N.md`. Rendered to HTML via `docs/templates/render-slides.py`.

## Workflow

1. Claude generates the phase markdown from the plan + notes. Keep it to 5–10 slides.
2. Render:
   ```bash
   python3 docs/templates/render-slides.py \
     docs/slides/<topic>/phase-N.md \
     docs/slides/<topic>/phase-N.html
   ```
3. Start the static server (`.claude/launch.json` → `static-server`) and open:
   `http://localhost:8000/docs/slides/<topic>/phase-N.html`

## Slide format

```markdown
# <Phase Title>

One-line hook.

---

## Slide 2 title

- point
- point

```mermaid
graph LR
  A --> B
```
```

Slides split on a line containing only `---`. Use Mermaid for diagrams where flow matters.

## Why per-phase (not per-session)

Decks summarise a phase's key concepts once. Sessions within the phase apply those concepts through exercises; they don't each need their own deck. This was the main course-correction from the first draft of this structure (see `/home/joeyang/.claude/plans/wild-skipping-mango.md`).
