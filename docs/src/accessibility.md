# Accessibility statement

This page states the accessibility posture of the AI Agent Assembly
documentation hub for readers — and for procurement or compliance reviewers —
who need a public statement of intent before adopting the product.

## Conformance target

We are **working toward [WCAG 2.1](https://www.w3.org/TR/WCAG21/) Level AA**
for this documentation site. This is a target we are actively pursuing, not a
certified conformance claim. As gaps are found they are tracked and fixed
rather than waived.

## What we do today

- **Semantic, keyboard-navigable content.** The site is built with
  [mdBook](https://rust-lang.github.io/mdBook/), which renders plain semantic
  HTML with a keyboard-operable sidebar, search, and theme controls.
- **Readable contrast in light and dark.** The default light theme and the
  dark themes aim to meet the WCAG AA contrast ratio for body text.
- **Text alternatives.** Informative images carry alternative text, and
  architecture diagrams are accompanied by a prose or tabular description so
  the same information is available without seeing the diagram.
- **Resizable, reflowable text.** Content reflows without loss of information
  when zoomed or viewed on a narrow screen.

## Known limitations

- Some **Mermaid** diagrams are rendered as SVG; where a diagram is essential
  we provide an adjacent text description, but not every diagram has full
  alternative markup yet.
- The site depends on the upstream mdBook theme; a small number of its
  controls may not yet fully meet AA, and we track those upstream.

## Feedback

If you hit an accessibility barrier on this site, please
[open an issue on the docs repository](https://github.com/ai-agent-assembly/docs/issues/new/choose).
Tell us the page, what you were trying to do, and the assistive technology or
browser you were using — we treat accessibility barriers as bugs.
