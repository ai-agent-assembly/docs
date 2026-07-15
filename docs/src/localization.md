# Localization

**This documentation is English-only for now, and localization contributions
are welcome.** This page states that policy for readers evaluating the product
worldwide, and records the plan for adding translations when they are
prioritized. No translated content ships yet — this is a scaffold and plan, not
a live multilingual site.

## Current status

- All pages on this hub and on the marketing site are authored in English (`en`).
- There is no language switcher yet; the mdBook chrome exposes only theme and
  search controls.
- Translation is **deferred** — see the plan below for how it will be enabled.

## How localization will work (plan)

When translations are prioritized, this hub will adopt mdBook's
gettext-based localization via the
[`mdbook-i18n-helpers`](https://github.com/google/mdbook-i18n-helpers)
toolchain, which is the standard approach for multilingual mdBook sites:

1. **Extract** the English source into a `messages.pot` template with
   `mdbook-xgettext`.
2. **Translate** per-language `po/<lang>.po` catalogs (for example
   `po/zh-TW.po`, `po/ja.po`, `po/es.po`), contributed by the community.
3. **Build** one localized site per language by pointing the renderer at the
   corresponding catalog, and surface a language switcher in the theme.

The book's source language stays `en`; translations are layered on top as PO
catalogs so the English content remains the single source of truth and cannot
drift silently from its translations.

A commented `# [language]` scaffold block in `docs/book.toml` marks where the
per-language configuration will live once this is enabled.

> **Marketing site.** The marketing site (`agent-assembly.com`) is built with
> Docusaurus, which has its own [built-in i18n](https://docusaurus.io/docs/i18n/introduction).
> Enabling localization there is tracked separately from this docs hub; this
> plan covers the mdBook documentation hub only.

## Contributing a translation

Translations are community-contributed. If you would like to help localize the
documentation, please
[open an issue on the docs repository](https://github.com/ai-agent-assembly/docs/issues/new/choose)
naming the language you want to work on, so we can coordinate before wiring up
the PO-catalog workflow above.
