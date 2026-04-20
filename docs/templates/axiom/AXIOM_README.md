# Axiom Design System

A minimalist, academic design system for **interactive self-study learning materials** — slides for concepts, and interactive visualizations for tricky ideas like C++ memory layouts, tree traversals (DFS/BFS), graph algorithms, and data plots.

The system is tuned for **science, computer science, and engineering** content. It reads like a well-typeset technical book, behaves like a precise engineering notebook, and uses a single restrained accent color so *diagrams* carry the visual weight instead of UI chrome.

## Sources & provenance

This system was created **without an attached codebase, Figma file, or reference brand**. The user described:

- Purpose: interactive learning materials for self-study
- Formats: slides for concepts, interactive charts/graphs for complex topics (C++ memory, DFS on a tree, etc.)
- Content domain: science, CS, engineering
- Aesthetic direction: **minimalist, clean**

No external Figma links, codebases, or asset archives were provided. If a reference becomes available later, re-run the system against it to lock visuals more tightly.

**Font substitutions (flag):** Since no fonts were provided, the system uses Google Fonts substitutions:
- **Source Serif 4** — display/long-form serif (substitute for any licensed academic serif like Charter, Tiempos, or Lyon)
- **Inter Tight** — body sans (substitute for any neo-grotesque)
- **JetBrains Mono** — code/mono (safe, open)

→ If you own different faces, drop the files into `fonts/` and update `@import` in `colors_and_type.css`.

## Index

```
Axiom/
├── README.md              ← you are here
├── SKILL.md               ← agent skill entrypoint (cross-compatible w/ Claude Code)
├── colors_and_type.css    ← CSS variables: colors, type, spacing, radii, shadows, motion
├── assets/
│   ├── logo.svg           ← Axiom wordmark
│   ├── logo-mark.svg      ← Axiom mark (A glyph)
│   └── icons.md           ← iconography notes (uses Lucide via CDN)
├── preview/               ← cards shown in the Design System review tab
│   ├── type-*.html
│   ├── colors-*.html
│   ├── spacing-*.html
│   ├── components-*.html
│   └── brand-*.html
├── slides/                ← slide templates for learning concepts
│   ├── index.html         ← interactive deck sample
│   └── *.jsx              ← TitleSlide, ConceptSlide, DiagramSlide, CodeSlide, …
└── ui_kits/
    ├── slides/            ← same as /slides — duplicated here for the kit index
    └── visualizations/    ← interactive charts, memory layouts, graph traversals
        ├── index.html
        └── *.jsx
```

---

## Content fundamentals

Axiom writes like a **patient, precise teacher**. The tone is that of a knowledgeable peer who is excited about the material — never a marketer, never a textbook drone.

### Voice
- **Second person, mostly.** "You can see the pointer now lives on the stack." Not "The user can see…"
- **First-person plural** for derivations, walkthroughs. "Let's expand this step." "We'll skip the algebra and plot both curves."
- **Avoid 'I'** — the content is not a personal essay.

### Tone
- **Curious and unhurried.** Explain *why*, not just *what*.
- **Comfortable with pauses.** Short sentences are fine. One idea at a time.
- **Never hype.** No "amazing", "powerful", "game-changing", "revolutionary".
- **Never apologetic.** No "this might be confusing…" — if it's confusing, fix the exposition.

### Casing
- **Sentence case everywhere.** Headings, buttons, captions, menus. *"Memory layout of a struct"*, not *"Memory Layout of a Struct"*.
- **Code identifiers keep their source casing** — `std::vector`, `useEffect`, `O(n log n)`.
- **Acronyms uppercase** — DFS, BFS, CPU, RAM, JSON.

### Punctuation
- Em-dashes (`—`) for parenthetical asides. Use real em-dashes, not `--`.
- Mathematical notation prefers Unicode: `→`, `≤`, `≥`, `≠`, `∑`, `∞`, `π`, `θ`.
- Code inline uses backticks; no "quoted" code.

### Emoji
- **No emoji.** The system is typographic — Unicode arrows/math symbols cover every need emoji would.

### Example copy

> **Concept title (serif, sentence case)**
> A one-sentence framing of what's about to happen.
>
> When we allocate a `std::vector<int>` on the stack, three pointers — `begin`, `end`, `capacity` — live in the stack frame. The actual elements sit on the heap. Drag the slider below to push values and watch the capacity double.
>
> *Note:* capacity growth is implementation-defined; libc++ doubles, libstdc++ doubles, MSVC grows by 1.5×.

### Patterns
- **Definitions** are set in *italic serif*, followed by the definition in body sans.
- **Figures** have a numbered caption in small caps: `FIG. 1  — Stack and heap after push_back(42)`.
- **Callouts** are single-colored, single-lined; we never stack multiple colored alert boxes.
- **Side notes** use a thin left rule and italic type — never a colored card.

---

## Visual foundations

The system is built to **stay out of the way of the content**. Diagrams, equations, and code are the subject; UI is the frame.

### Colors

A **warm paper + cool technical** palette:
- **Paper** off-white `#fbfaf7` page, `#f4f1ea` for cards/wash. Warm, reduces eye strain in long sessions.
- **Ink** `#171512` primary text — a true book-black with a hint of warmth. Never pure `#000`.
- **Accent** a single muted indigo `#3b4cad`. Used for links, selection, one highlight per diagram. Never as a decorative gradient.
- **Semantic** red/amber/green/teal — muted, academic, never neon. Green for correct, red for incorrect/error, amber for caution, teal for secondary info.
- **Viz palette** 7 colorblind-friendly hues for charts. First color is always the accent; subsequent colors walk a hue circle.
- **Dark mode** cool slate `#0f1216` bg with `#ecebe6` text — designed for late-night study.

Full palette and tokens are in `colors_and_type.css`.

### Typography
- **Serif — Source Serif 4** for H1/H2/H3, lead paragraphs, definitions, blockquotes. Readable at both display and body sizes.
- **Sans — Inter Tight** for body, UI, captions, labels, data labels.
- **Mono — JetBrains Mono** for code blocks, inline code, memory addresses, register names.
- **Scale**: 12/14/16/18/21/26/32/42/56/72 px. 1.2 ratio, anchored at 16.
- **Line length** caps at `68ch` for body prose. Never full-bleed text.

### Spacing
4px base grid. Tokens: `--sp-1`..`--sp-10` (4 → 128). Most screens live on 8/16/24/32. Slides breathe at 48/64/96.

### Backgrounds
- **Never gradients.** The system uses flat warm paper or flat slate.
- **Never full-bleed photographic imagery** in the core UI. Diagrams are SVG on paper.
- **Optional**: subtle paper grain can be applied to slide backgrounds via a low-opacity noise SVG (not included by default).

### Animation
- **Short, confident, purposeful.** `120ms` for hover state changes, `200ms` for panel/menu, `320ms` for slide transitions, `500ms` only for teaching moments (e.g. a node highlighting on a graph during DFS).
- **Easing** `cubic-bezier(0.2, 0.6, 0.2, 1)` — a gentle out. No bounces. No spring physics.
- **Interactive diagrams** animate *state* (a pointer moving, a stack frame highlighting), not chrome.

### Hover & press
- **Hover**: 1 step darker background / border. Never a glow, never a shadow lift.
- **Press**: `transform: scale(0.98)` OR no motion at all; prefers darker background.
- **Focus**: 2px accent outline, offset 2px. Always visible, always the same.

### Borders
- Hairline `1px solid var(--border)` (warm paper-200). Strong variant for when a card needs to *assert* itself.
- Diagram strokes use `--ink-700` at 1.5px — slightly heavier than UI hairlines so shapes read from across the room.

### Shadows
Almost never used. Three tiers exist (`--shadow-1/2/3`) for menus and modals only. Cards use **borders, not shadows**. Surface elevation is conveyed by color (paper → card white) not lift.

### Transparency & blur
- **Blur**: never in the base UI. Optional on slide progress overlays (`backdrop-filter: blur(8px)`).
- **Transparency**: on hover/selection states only (~10% accent wash).

### Imagery
- Diagrams, not photos. Line drawings, not gradients.
- If photos are used (rare), they are **desaturated slightly** (`filter: saturate(0.85)`) to sit next to the paper background without fighting.

### Corner radii
- **Cards, buttons, inputs**: `6px` (`--r-3`). Just enough to feel modern without being playful.
- **Tags, badges**: `4px`.
- **Avatars, circles**: `9999px`.
- **Sharp edges** (0px) used in code blocks and terminal surfaces for a more technical feel.

### Cards
Flat. White (`--bg-raised`) on paper background. `1px solid var(--border)`. 6px radius. No shadow. Internal padding `--sp-5` (24px).

### Layout rules
- Content lives within a `1120px` container, left-aligned on wide screens (not centered text columns).
- Sidebars snap to `280px`, navigation bars to `56px` tall.
- Slides are `1920×1080` (16:9), scaled to fit the viewport via the `deck_stage` starter component.

---

## Iconography

Axiom uses **Lucide** via CDN — clean 1.5px-stroke line icons. They match the system's typographic feel and avoid the filled-rounded look of Material/Heroicons-solid.

```html
<script src="https://unpkg.com/lucide@latest"></script>
<i data-lucide="circle-play"></i>
<script>lucide.createIcons();</script>
```

Or inline SVGs copied from https://lucide.dev/icons — each icon is a ~1KB SVG.

### Icon rules
- **Size**: 16px (inline), 20px (buttons), 24px (headers), 32px+ for empty states.
- **Stroke**: 1.5px (Lucide default). Never change this — inconsistent stroke weight is the most common icon-system smell.
- **Color**: inherit `currentColor` from text. Accent only on active/selected state.
- **Never emoji.** Even for decorative purposes.
- **Unicode math/arrows** (`→`, `←`, `↔`, `∴`, `≈`) are used inline for teaching content; icons are for UI chrome only.

### Flag
The Axiom wordmark and mark are **original minimalist drawings** created for this system (see `assets/logo.svg`, `assets/logo-mark.svg`). If you have a real logo to swap in, replace those files and the rest of the system will adapt.

---

## Using the system

Add the stylesheet and wrap your page in `.axiom`:

```html
<link rel="stylesheet" href="colors_and_type.css">
<body class="axiom">
  <h1>Memory layout of a struct</h1>
  <p class="lead">Three fields, two of them padded.</p>
  <pre><code>struct Point { int x; char c; double z; };</code></pre>
</body>
```

Toggle dark mode by setting `data-theme="dark"` on any ancestor.
