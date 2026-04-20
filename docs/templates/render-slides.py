#!/usr/bin/env python3
"""Render a markdown file into a single-page HTML slide deck.

Uses the vendored Axiom design system under docs/templates/axiom/:
 - colors_and_type.css for design tokens (fonts, palette, spacing)
 - deck-stage.js for the <deck-stage> web component (keyboard nav,
   localStorage, print-to-PDF, 1920x1080 auto-scaled canvas)

Usage:
    python3 render-slides.py <input.md> <output.html>
        [--title "Deck Title"] [--eyebrow "topic · phase 1"]

Assets are referenced at absolute paths /docs/templates/axiom/* so the
generated HTML must be served from the repo root (.claude/launch.json
serves it on :8000). Opening via file:// will miss the stylesheet.

Slide separator: a line containing only `---` (three dashes).
The first slide is emitted with class `slide is-title` — large serif
title + italic lead paragraph. Override per slide with a directive
comment on the first line of the slide:

    <!-- class: is-dark -->       # dark summary
    <!-- class: is-section -->    # warm wash section divider
    <!-- class: is-quote -->      # big italic pull quote

Supported markdown: headers (# ## ###), bold, italic, inline code,
links, unordered/ordered lists, blockquotes, pipe tables, fenced code
blocks (```lang). A ```mermaid fence renders as a diagram via CDN.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

# Axiom's Lucide-style wordmark glyph, inlined so each slide's rail is
# self-contained (no image request per slide).
LOGO_MARK_SVG = (
    '<svg class="mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">'
    '<g stroke="currentColor" stroke-width="2.5" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<path d="M10 40 L24 8 L38 40"/><path d="M16 28 L32 28"/>'
    '</g></svg>'
)

HTML_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="/docs/templates/axiom/colors_and_type.css">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  /* Deck background (visible as letterbox around the scaled canvas). */
  html, body {{ margin: 0; padding: 0; background: #000; height: 100%; }}
  body.axiom {{ font-family: var(--font-sans); }}

  /* ---- Slide surface (from Axiom ui_kits/slides/index.html) -------- */
  .slide {{
    background: var(--bg);
    color: var(--fg-1);
    /* top right bottom left — bottom is bigger so content doesn't collide
       with the absolutely-positioned .foot at bottom: 48px. */
    padding: 128px 128px 152px;
    display: flex;
    flex-direction: column;
    position: relative;
    box-sizing: border-box;
    overflow: hidden;
  }}
  .slide.is-title   {{ padding: 160px 160px 180px; }}
  .slide.is-section {{ background: var(--paper-100); }}
  .slide.is-dark    {{ background: #0f1216; color: #ecebe6; }}
  .slide.is-quote   {{ padding: 200px 200px 180px; }}
  .slide.is-dark .rail, .slide.is-dark .page-num,
  .slide.is-dark .foot {{ color: #8f8b7f; }}
  .slide.is-dark pre  {{ background: #0a0c10; border-color: #23272e; color: #ecebe6; }}
  .slide.is-dark code {{ background: #161a20; border-color: #23272e; color: #ecebe6; }}
  .slide.is-dark blockquote {{ color: #c2bfb5; border-color: #3b4cad; }}
  .slide.is-dark .fig {{ background: #161a20; border-color: #23272e; }}

  /* ---- Typography — markdown tags get slide-scale styles by default. */
  .slide h1 {{
    font-family: var(--font-serif); font-weight: 400;
    font-size: 96px; line-height: 1.05; letter-spacing: -0.02em;
    margin: 0 0 48px; max-width: 1500px; color: var(--fg-1);
  }}
  .slide.is-title h1 {{ font-size: 128px; }}
  .slide.is-dark h1, .slide.is-dark h2, .slide.is-dark h3 {{ color: #ecebe6; }}
  .slide h2 {{
    font-family: var(--font-serif); font-weight: 400;
    font-size: 56px; line-height: 1.1; letter-spacing: -0.02em;
    margin: 0 0 32px; max-width: 1500px; color: var(--fg-1);
  }}
  .slide h3 {{
    font-family: var(--font-serif); font-weight: 500;
    font-size: 36px; line-height: 1.2; letter-spacing: -0.01em;
    margin: 24px 0 16px; color: var(--fg-1);
  }}
  .slide p {{
    font-family: var(--font-sans); font-size: 28px; line-height: 1.5;
    color: inherit; max-width: 1500px; margin: 0 0 20px;
  }}
  /* First paragraph right after a title-slide H1 becomes the italic lead. */
  .slide.is-title h1 + p {{
    font-family: var(--font-serif); font-style: italic;
    font-size: 40px; line-height: 1.3; color: var(--fg-2);
  }}
  .slide ul, .slide ol {{ margin: 0 0 24px; padding: 0; max-width: 1500px; }}
  .slide ul {{ list-style: none; }}
  .slide ul li {{
    position: relative; padding-left: 36px; margin-bottom: 14px;
    font-family: var(--font-sans); font-size: 28px; line-height: 1.4;
  }}
  .slide ul li::before {{
    content: ''; position: absolute; left: 0; top: 0.65em;
    width: 18px; height: 2px; background: var(--fg-3);
  }}
  .slide ol {{ padding-left: 44px; }}
  .slide ol li {{
    font-family: var(--font-sans); font-size: 28px; line-height: 1.4;
    margin-bottom: 14px;
  }}
  .slide code {{
    font-family: var(--font-mono); font-size: 0.85em;
    background: var(--bg-code); padding: 2px 10px;
    border-radius: 4px; color: var(--fg-1);
    border: 1px solid var(--border);
  }}
  .slide pre {{
    font-family: var(--font-mono); font-size: 24px; line-height: 1.5;
    background: var(--syn-bg); color: var(--syn-text);
    padding: 28px 36px; border: 1px solid var(--border);
    border-radius: 6px; overflow: auto; margin: 0 0 24px;
    max-width: 1500px;
  }}
  .slide pre code {{ background: transparent; padding: 0; border: 0; font-size: inherit; }}
  .slide blockquote {{
    border-left: 2px solid var(--border-accent);
    padding: 8px 32px; margin: 24px 0;
    font-family: var(--font-serif); font-style: italic;
    font-size: 32px; line-height: 1.4; color: var(--fg-2);
    max-width: 1500px;
  }}
  .slide blockquote p {{ font-family: inherit; font-size: inherit; font-style: inherit; color: inherit; margin: 0; }}
  .slide a {{ color: var(--link); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
  .slide strong {{ font-weight: 600; color: inherit; }}
  .slide em {{ font-style: italic; }}

  /* ---- Tables ------------------------------------------------------- */
  .slide table {{
    border-collapse: collapse; margin: 16px 0 24px;
    font-family: var(--font-sans); font-size: 24px; line-height: 1.4;
    max-width: 1500px;
  }}
  .slide th, .slide td {{ padding: 14px 22px; text-align: left; border-bottom: 1px solid var(--border); }}
  .slide th {{ font-weight: 600; border-bottom: 1.5px solid var(--ink-700); color: var(--fg-1); }}

  /* ---- Slide chrome (rail / page-num / foot) ------------------------ */
  .slide .rail {{
    position: absolute; left: 128px; top: 48px;
    display: flex; align-items: center; gap: 14px;
    font-family: var(--font-mono); font-size: 18px;
    color: var(--fg-3); letter-spacing: 0.04em;
  }}
  .slide .rail .mark {{ width: 22px; height: 22px; color: inherit; }}
  .slide .page-num {{
    position: absolute; right: 128px; top: 48px;
    font-family: var(--font-mono); font-size: 18px;
    color: var(--fg-3); letter-spacing: 0.04em;
  }}
  .slide .foot {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 36px 128px 48px;
    background: var(--bg);
    display: flex; justify-content: space-between;
    font-family: var(--font-mono); font-size: 18px;
    color: var(--fg-4); letter-spacing: 0.04em;
  }}
  .slide.is-section .foot {{ background: var(--paper-100); }}
  .slide.is-dark .foot    {{ background: #0f1216; }}

  /* ---- Figure frame for diagrams ------------------------------------ */
  .slide .fig {{
    background: var(--bg-raised); border: 1px solid var(--border);
    border-radius: 8px; padding: 28px; margin: 16px 0 24px;
    max-width: 1500px;
  }}
  .slide .mermaid {{ background: transparent; text-align: center; }}
</style>
</head>
<body class="axiom">
<deck-stage width="1920" height="1080">
{slides}
</deck-stage>
<script src="/docs/templates/axiom/deck-stage.js"></script>
<script>
  // Mermaid renders when a slide may be visibility:hidden (but still has
  // 1920x1080 geometry inside the deck canvas), so normally diagrams
  // measure correctly. Still, strip any baked-in max-width style as a
  // safety net so the SVG can scale with its container on theme changes.
  function fixMermaidSizes() {{
    document.querySelectorAll('.mermaid svg').forEach((svg) => {{
      svg.style.maxWidth = '100%';
      svg.style.width = '100%';
      svg.style.height = 'auto';
    }});
  }}
  if (window.mermaid) {{
    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
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
    code_spans: list[str] = []
    def _stash_code(m: re.Match[str]) -> str:
        code_spans.append(html.escape(m.group(1)))
        return f"\x00{len(code_spans) - 1}\x00"
    text = re.sub(r"`([^`]+)`", _stash_code, text)

    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    def _unstash(m: re.Match[str]) -> str:
        return f"<code>{code_spans[int(m.group(1))]}</code>"
    return re.sub(r"\x00(\d+)\x00", _unstash, text)


def _render_table(rows: list[str]) -> str:
    """Pipe-table syntax: first row = header, second row = alignment, rest = body."""
    def _cells(row: str) -> list[str]:
        row = row.strip().strip("|")
        return [c.strip() for c in row.split("|")]

    header = _cells(rows[0])
    body_rows = [_cells(r) for r in rows[2:]]
    thead = "".join(f"<th>{_inline(c)}</th>" for c in header)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
        for r in body_rows
    )
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>"


def _render_block(lines: list[str]) -> str:
    """Convert a list of markdown lines (one slide's body) to HTML."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block (handles mermaid specially).
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            lang = m.group(1) or ""
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            code = "\n".join(body)
            if lang == "mermaid":
                out.append(f'<div class="fig"><div class="mermaid">{html.escape(code)}</div></div>')
            else:
                out.append(
                    f'<pre><code class="language-{html.escape(lang)}">'
                    f"{html.escape(code)}</code></pre>"
                )
            continue

        # Headers.
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Pipe table (header, |---|---|, then body rows).
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]
        ):
            table_rows: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table_rows.append(lines[i])
                i += 1
            out.append(_render_table(table_rows))
            continue

        # Blockquote.
        if line.startswith("> "):
            quote: list[str] = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(quote))}</blockquote>")
            continue

        # Unordered list.
        if re.match(r"^\s*[-*]\s+", line):
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        # Ordered list.
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(_inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
            continue

        if not line.strip():
            i += 1
            continue

        # Paragraph (greedy over non-special non-blank lines).
        para: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,3}\s|>\s|\s*[-*]\s|\s*\d+\.\s|```|\|)", lines[i]
        ):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{_inline(' '.join(para))}</p>")

    return "\n".join(out)


def _slide_label(chunk: str, fallback_n: int) -> str:
    """Derive a short slide label from the first heading, capped at 40 chars."""
    m = re.search(r"^#+\s+(.+)$", chunk, re.MULTILINE)
    if m:
        return m.group(1).strip()[:40]
    return f"Slide {fallback_n}"


def _render_slide(chunk: str, n: int, total: int, eyebrow: str, deck_title: str) -> str:
    """Emit one <section class="slide ..."> with Axiom chrome."""
    extra_classes: list[str] = []

    # Directive: <!-- class: is-dark --> on the first non-blank line.
    dir_match = re.match(r"^\s*<!--\s*class:\s*([\w\s-]+?)\s*-->\s*\n?", chunk)
    if dir_match:
        extra_classes = dir_match.group(1).strip().split()
        chunk = chunk[dir_match.end():]
    elif n == 1:
        extra_classes.append("is-title")

    label = _slide_label(chunk, n)
    body = _render_block(chunk.splitlines())

    class_attr = " ".join(["slide"] + extra_classes)
    page_num = f"{n:02d} / {total:02d}"
    return (
        f'<section class="{class_attr}" data-label="{html.escape(label)}">'
        f'<div class="rail">{LOGO_MARK_SVG}<span>{html.escape(eyebrow)}</span></div>'
        f'<div class="page-num">{page_num}</div>'
        f"{body}"
        f'<div class="foot"><span>{html.escape(deck_title)}</span>'
        f"<span>{page_num}</span></div>"
        f"</section>"
    )


def render(md_source: str, title: str | None = None, eyebrow: str | None = None) -> str:
    """Render markdown source into a full HTML slide deck."""
    slide_chunks = re.split(r"^---\s*$", md_source, flags=re.MULTILINE)
    slide_chunks = [c.strip("\n") for c in slide_chunks if c.strip()]

    if title is None:
        m = re.search(r"^#\s+(.*)$", slide_chunks[0] if slide_chunks else "", re.MULTILINE)
        title = m.group(1).strip() if m else "Slide Deck"
    if eyebrow is None:
        eyebrow = f"axiom · {title.lower()}"

    total = len(slide_chunks)
    slide_htmls = [
        _render_slide(chunk, i + 1, total, eyebrow, title)
        for i, chunk in enumerate(slide_chunks)
    ]
    return HTML_SHELL.format(title=html.escape(title), slides="\n".join(slide_htmls))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path, help="Input markdown file")
    parser.add_argument("output", type=Path, help="Output HTML file")
    parser.add_argument("--title", default=None, help="Deck title (defaults to first H1)")
    parser.add_argument("--eyebrow", default=None, help="Rail eyebrow text (defaults to 'axiom · <title>')")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1

    md = args.input.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(md, args.title, args.eyebrow), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
