#!/usr/bin/env python3
"""Render a markdown file into a single-page HTML slide deck.

Usage:
    python3 render-slides.py <input.md> <output.html> [--title "Deck Title"]

Slide separator: a line containing only `---` (three dashes).
The first slide's first H1 is used as the deck title if --title not given.

Supports a minimal but useful markdown subset:
    # H1  ## H2  ### H3
    **bold**  *italic*  `inline code`
    [link](url)
    - unordered list items
    1. ordered list items
    > blockquote
    ```lang ... ```  (fenced code; `mermaid` renders as a diagram)
    blank-line-separated paragraphs

The rendered deck has keyboard navigation (arrow keys / space), progress
dots, a slide counter, and a light/dark theme toggle.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  :root {{
    --bg: #0f1115; --fg: #e6e6e6; --muted: #8a8f98; --accent: #7aa2f7;
    --code-bg: #1a1d24; --border: #2a2f3a;
  }}
  [data-theme="light"] {{
    --bg: #fafafa; --fg: #1b1b1f; --muted: #5a5f68; --accent: #2c5fd6;
    --code-bg: #f1f2f6; --border: #d8dbe0;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; height: 100%; }}
  body {{
    background: var(--bg); color: var(--fg); font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6; overflow: hidden;
  }}
  #deck {{ height: 100vh; width: 100vw; position: relative; }}
  section.slide {{
    position: absolute; inset: 0; padding: 4rem 6rem 6rem; overflow: auto;
    display: none; flex-direction: column;
  }}
  section.slide.active {{ display: flex; }}
  h1 {{ font-size: 2.4rem; margin: 0 0 1.5rem; color: var(--accent); }}
  h2 {{ font-size: 1.8rem; margin: 0 0 1.2rem; color: var(--accent); }}
  h3 {{ font-size: 1.3rem; margin: 1rem 0 0.6rem; }}
  p  {{ font-size: 1.15rem; margin: 0.5rem 0; }}
  ul, ol {{ font-size: 1.1rem; padding-left: 1.6rem; }}
  li {{ margin: 0.3rem 0; }}
  code {{
    background: var(--code-bg); padding: 0.1rem 0.4rem; border-radius: 3px;
    font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.95em;
  }}
  pre {{
    background: var(--code-bg); padding: 1rem; border-radius: 6px;
    overflow: auto; font-size: 0.92rem; border: 1px solid var(--border);
  }}
  pre code {{ background: transparent; padding: 0; }}
  blockquote {{
    margin: 1rem 0; padding: 0.4rem 1rem; border-left: 4px solid var(--accent);
    color: var(--muted); font-style: italic;
  }}
  a {{ color: var(--accent); }}
  .mermaid {{
    background: var(--code-bg); padding: 1rem; border-radius: 6px;
    border: 1px solid var(--border); text-align: center;
  }}
  #chrome {{
    position: fixed; bottom: 0; left: 0; right: 0; padding: 0.8rem 1.2rem;
    display: flex; align-items: center; gap: 1rem; background: var(--bg);
    border-top: 1px solid var(--border);
  }}
  #dots {{ flex: 1; display: flex; gap: 0.4rem; justify-content: center; }}
  #dots button {{
    width: 10px; height: 10px; border-radius: 50%; padding: 0;
    background: var(--border); border: none; cursor: pointer;
  }}
  #dots button.active {{ background: var(--accent); }}
  #counter {{ color: var(--muted); font-family: ui-monospace, Menlo, monospace; font-size: 0.9rem; }}
  .btn {{
    background: var(--code-bg); color: var(--fg); border: 1px solid var(--border);
    padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 1rem;
  }}
  .btn:hover {{ border-color: var(--accent); }}
</style>
</head>
<body data-theme="dark">
<div id="deck">{slides}</div>
<div id="chrome">
  <button class="btn" id="prev" aria-label="Previous">&larr;</button>
  <div id="dots"></div>
  <span id="counter">1 / 1</span>
  <button class="btn" id="next" aria-label="Next">&rarr;</button>
  <button class="btn" id="theme" aria-label="Toggle theme">&#9728;</button>
</div>
<script>
  const slides = document.querySelectorAll('section.slide');
  const dots = document.getElementById('dots');
  const counter = document.getElementById('counter');
  let current = 0;

  slides.forEach((_, i) => {{
    const b = document.createElement('button');
    b.addEventListener('click', () => show(i));
    dots.appendChild(b);
  }});

  function show(i) {{
    current = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((s, idx) => s.classList.toggle('active', idx === current));
    dots.querySelectorAll('button').forEach((d, idx) => d.classList.toggle('active', idx === current));
    counter.textContent = (current + 1) + ' / ' + slides.length;
    history.replaceState(null, '', '#' + (current + 1));
  }}

  document.getElementById('prev').addEventListener('click', () => show(current - 1));
  document.getElementById('next').addEventListener('click', () => show(current + 1));
  document.getElementById('theme').addEventListener('click', () => {{
    const cur = document.body.dataset.theme;
    document.body.dataset.theme = cur === 'dark' ? 'light' : 'dark';
    if (window.mermaid) mermaid.initialize({{ theme: document.body.dataset.theme === 'dark' ? 'dark' : 'default' }});
  }});
  document.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowRight' || e.key === ' ') {{ show(current + 1); e.preventDefault(); }}
    else if (e.key === 'ArrowLeft') {{ show(current - 1); e.preventDefault(); }}
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
  }});

  const start = parseInt((location.hash || '#1').slice(1), 10) - 1;
  show(isNaN(start) ? 0 : start);

  // Mermaid renders at load time when most slides are display:none, which
  // causes SVGs to bake in a tiny max-width. Strip that so the SVG can
  // scale to its container once the slide becomes visible.
  function fixMermaidSizes() {{
    document.querySelectorAll('.mermaid svg').forEach((svg) => {{
      svg.style.maxWidth = '100%';
      svg.style.width = '100%';
      svg.style.height = 'auto';
    }});
  }}

  if (window.mermaid) {{
    mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
    // mermaid.run() resolves once diagrams are processed; on older versions
    // fall back to a short delay.
    if (typeof mermaid.run === 'function') {{
      mermaid.run().then(fixMermaidSizes).catch(fixMermaidSizes);
    }} else {{
      setTimeout(fixMermaidSizes, 500);
    }}
  }}
</script>
</body>
</html>
"""


def _inline(text: str) -> str:
    """Convert inline markdown (code, bold, italic, links) to HTML."""
    # Protect inline code spans first
    code_spans: list[str] = []
    def _stash_code(m: re.Match[str]) -> str:
        code_spans.append(html.escape(m.group(1)))
        return f"\x00{len(code_spans) - 1}\x00"
    text = re.sub(r"`([^`]+)`", _stash_code, text)

    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    # Restore code spans
    def _unstash(m: re.Match[str]) -> str:
        return f"<code>{code_spans[int(m.group(1))]}</code>"
    return re.sub(r"\x00(\d+)\x00", _unstash, text)


def _render_block(lines: list[str]) -> str:
    """Convert a list of markdown lines (one slide's body) to HTML."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            lang = m.group(1) or ""
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            if lang == "mermaid":
                out.append(f'<div class="mermaid">{html.escape(chr(10).join(body))}</div>')
            else:
                out.append(f'<pre><code class="language-{html.escape(lang)}">{html.escape(chr(10).join(body))}</code></pre>')
            continue

        # Headers
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(quote))}</blockquote>")
            continue

        # Unordered list
        if re.match(r"^\s*[-*]\s+", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (accumulate consecutive non-blank non-special lines)
        para: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s|>\s|\s*[-*]\s|\s*\d+\.\s|```)", lines[i]
        ):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")

    return "\n".join(out)


def render(md_source: str, title: str | None = None) -> str:
    """Render markdown source into a full HTML slide deck."""
    slide_chunks = re.split(r"^---\s*$", md_source, flags=re.MULTILINE)
    slide_chunks = [c.strip("\n") for c in slide_chunks if c.strip()]

    if title is None:
        m = re.search(r"^#\s+(.*)$", slide_chunks[0] if slide_chunks else "", re.MULTILINE)
        title = m.group(1).strip() if m else "Slide Deck"

    slides_html = "\n".join(
        f'<section class="slide">{_render_block(chunk.splitlines())}</section>'
        for chunk in slide_chunks
    )
    return HTML_SHELL.format(title=html.escape(title), slides=slides_html)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Input markdown file")
    parser.add_argument("output", type=Path, help="Output HTML file")
    parser.add_argument("--title", default=None, help="Deck title (defaults to first H1)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1

    md = args.input.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(md, args.title), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
