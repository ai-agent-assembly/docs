# Localization

**This documentation is authored in English, and Traditional Chinese
(繁體中文, `zh-Hant`) is available as a first-pass translation of the priority
pages.** This page states that policy for readers evaluating the product
worldwide and records how translations are produced and contributed. Additional
languages are welcome — see the contributor workflow below.

## Current status

- The English source (`en`) is the single source of truth for every page.
- **繁體中文 (`zh-Hant`)** ships a **draft, machine first-pass** translation of
  the priority pages — the landing/introduction, the FAQ, the Glossary, and the
  Quick start (SaaS). Those pages carry a banner noting they are pending native
  review. Every other page falls back to English until it is translated.
- A **language switcher** in the page header (English ↔ 繁體中文) lets readers
  move between the two, page for page.

## How localization works

This hub uses mdBook's gettext-based localization via the
[`mdbook-i18n-helpers`](https://github.com/google/mdbook-i18n-helpers)
toolchain — the standard approach for multilingual mdBook sites. The English
source stays authoritative; each translation is layered on top as a PO catalog,
so English content cannot drift silently from its translations.

1. **Extract** the English source into a `po/messages.pot` template:

   ```sh
   cd docs
   MDBOOK_OUTPUT__xgettext__pot_file=messages.pot mdbook build -d po
   ```

2. **Translate** per-language `po/<lang>.po` catalogs (for example
   `po/zh-Hant.po`). Untranslated strings are left empty and fall back to the
   English source at build time.

3. **Build** one localized site per language by overriding the book language,
   which activates the `gettext` preprocessor (configured in `book.toml`):

   ```sh
   MDBOOK_BOOK__LANGUAGE=zh-Hant mdbook build -d book/zh-Hant
   ```

   The [aggregation pipeline](docs-hub-aggregation.md)
   (`docs/scripts/aggregate.sh`) builds English at the site root and each
   translated language under `/<lang>/` (e.g. `/zh-Hant/`), and the theme's
   language switcher links between them.

> **Toolchain note.** The default English build treats the `gettext`
> preprocessor as a no-op (there is no `po/en.po`), so contributors who only
> touch English content still just run `mdbook build`. Producing or previewing a
> translated build additionally requires the `mdbook-gettext` binary
> (`cargo install mdbook-i18n-helpers`).

## Contributing a translation

Translations are community-contributed. To improve the zh-Hant draft or add a
new language:

1. Re-sync the template if you changed English content (step 1 above), then
   merge it into the catalog you are editing:

   ```sh
   msgmerge --update po/zh-Hant.po po/messages.pot   # or msginit for a new language
   ```

2. Fill in the `msgstr` entries in `po/<lang>.po`. Use the
   [Glossary](glossary.md) to keep technical-term choices consistent, and keep
   product, crate, and API names (e.g. `aa-gateway`, `aa-proxy`, `aa-ebpf`,
   SDK and CLI identifiers) in English.
3. Validate with `msgfmt -c po/<lang>.po` and preview the localized build with
   the command in step 3 above before opening a PR.

If you would like to coordinate before starting, please
[open an issue on the docs repository](https://github.com/ai-agent-assembly/docs/issues/new/choose)
naming the language you want to work on.

> **Marketing site.** The marketing site (`agent-assembly.com`) is built with
> Docusaurus, which has its own [built-in i18n](https://docusaurus.io/docs/i18n/introduction).
> Enabling localization there is tracked separately from this docs hub; this
> workflow covers the mdBook documentation hub only.
