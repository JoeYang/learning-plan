"""Tests for render-slides.py.

Run with:  python3 -m unittest docs/templates/test_render_slides.py
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("render_slides", HERE / "render-slides.py")
assert SPEC and SPEC.loader
render_slides = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_slides)


class RenderTests(unittest.TestCase):
    def test_single_slide_wraps_in_section(self) -> None:
        html = render_slides.render("# Hello\n\nSome text.")
        self.assertEqual(html.count('<section class="slide">'), 1)
        self.assertIn("<h1>Hello</h1>", html)
        self.assertIn("<p>Some text.</p>", html)

    def test_slide_separator_splits_deck(self) -> None:
        md = "# One\n\n---\n\n# Two\n\n---\n\n# Three"
        html = render_slides.render(md)
        self.assertEqual(html.count('<section class="slide">'), 3)

    def test_title_defaults_to_first_h1(self) -> None:
        html = render_slides.render("# My Deck\n\nbody")
        self.assertIn("<title>My Deck</title>", html)

    def test_title_override_wins(self) -> None:
        html = render_slides.render("# Ignored\n", title="Chosen")
        self.assertIn("<title>Chosen</title>", html)

    def test_inline_formatting(self) -> None:
        html = render_slides.render("# T\n\n**bold** and *italic* and `code` and [link](https://x)")
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<code>code</code>", html)
        self.assertIn('<a href="https://x">link</a>', html)

    def test_unordered_list(self) -> None:
        html = render_slides.render("# T\n\n- one\n- two\n- three")
        self.assertIn("<ul><li>one</li><li>two</li><li>three</li></ul>", html)

    def test_ordered_list(self) -> None:
        html = render_slides.render("# T\n\n1. a\n2. b")
        self.assertIn("<ol><li>a</li><li>b</li></ol>", html)

    def test_fenced_code_block_is_escaped(self) -> None:
        md = "# T\n\n```python\nx = 1 < 2\n```"
        html = render_slides.render(md)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn("x = 1 &lt; 2", html)

    def test_mermaid_renders_as_diagram_div(self) -> None:
        md = "# T\n\n```mermaid\ngraph LR\nA-->B\n```"
        html = render_slides.render(md)
        self.assertIn('<div class="mermaid">', html)
        self.assertIn("A--&gt;B", html)

    def test_blockquote(self) -> None:
        html = render_slides.render("# T\n\n> quoted text")
        self.assertIn("<blockquote>quoted text</blockquote>", html)

    def test_headers_h1_h2_h3(self) -> None:
        html = render_slides.render("# T\n\n## Sub\n\n### SubSub")
        self.assertIn("<h1>T</h1>", html)
        self.assertIn("<h2>Sub</h2>", html)
        self.assertIn("<h3>SubSub</h3>", html)

    def test_html_in_content_is_escaped(self) -> None:
        html = render_slides.render("# T\n\n<script>alert(1)</script>")
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_empty_slides_are_dropped(self) -> None:
        html = render_slides.render("# One\n\n---\n\n\n\n---\n\n# Two")
        self.assertEqual(html.count('<section class="slide">'), 2)

    def test_mermaid_script_included(self) -> None:
        html = render_slides.render("# T")
        self.assertIn("mermaid", html.lower())


class CLITests(unittest.TestCase):
    def test_cli_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "input.md"
            dst = Path(d) / "sub" / "output.html"
            src.write_text("# Hi\n\n---\n\n# Bye\n")
            result = subprocess.run(
                [sys.executable, str(HERE / "render-slides.py"), str(src), str(dst)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(dst.exists())
            content = dst.read_text()
            self.assertEqual(content.count('<section class="slide">'), 2)

    def test_cli_missing_input_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dst = Path(d) / "output.html"
            result = subprocess.run(
                [sys.executable, str(HERE / "render-slides.py"), str(Path(d) / "missing.md"), str(dst)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("error", result.stderr.lower())
            self.assertFalse(dst.exists())


if __name__ == "__main__":
    unittest.main()
