# Interactive explainers

Standalone HTML pages for concepts that are genuinely dynamic — memory layout, order book depth, agent handoff flows. One file per concept, at `docs/interactive/<topic>/<concept>.html`.

## When to build one

- The concept benefits from motion or user input (drag, click, slider, timeline)
- A static slide with a diagram would lose the essence (flow, ordering, timing)

## When NOT to build one

- The concept is primarily textual (definitions, trade-off rules, facts)
- A Mermaid diagram in a slide would do the job — use that instead, it's cheaper

Default to a slide; upgrade to an interactive page only when motion actually adds insight.

## Hosting

Served via the static server at `http://localhost:8000/docs/interactive/<topic>/<concept>.html`. Prefer vanilla HTML/CSS/JS with CDN libraries for diagrams (Mermaid, d3) — no build step.
