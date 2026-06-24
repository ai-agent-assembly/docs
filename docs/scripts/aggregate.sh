#!/usr/bin/env bash
# Aggregate all module docs into a single static site under ./public (AAASM-3659).
#
# Pull/aggregate model: each module keeps its own generator. We build each
# module's DEFAULT channel (master/main HEAD) under /<subpath>/ with the correct
# subpath base URL, build the hub mdBook at root, then run Pagefind over the
# final public/ for unified search.
#
# Layout produced:
#   public/                 hub mdBook (index, concepts, guides, architecture, reference)
#   public/core/            agent-assembly core docs (mdBook)
#   public/python-sdk/      python-sdk docs (mkdocs-material)
#   public/node-sdk/        node-sdk docs (Docusaurus)
#   public/go-sdk/          go-sdk docs (Hugo + Hextra)
#   public/pagefind/        unified search index (Pagefind)
#
# Env:
#   MODULES_DIR   where to clone/find module repos (default: ./.modules)
#   PUBLIC_DIR    output dir (default: ./public)
#   SKIP_CLONE    if set, reuse existing checkouts under MODULES_DIR
#   SKIP_PAGEFIND if set, skip the Pagefind index step
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

MODULES_DIR="${MODULES_DIR:-$REPO_ROOT/.modules}"
PUBLIC_DIR="${PUBLIC_DIR:-$REPO_ROOT/public}"
REGISTRY="$REPO_ROOT/modules.json"

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

command -v jq      >/dev/null || fail "jq is required"
command -v mdbook  >/dev/null || fail "mdbook is required"

rm -rf "$PUBLIC_DIR"
mkdir -p "$PUBLIC_DIR" "$MODULES_DIR"

clone_module() {
  local repo="$1" ref="$2" dest="$3"
  if [[ -n "${SKIP_CLONE:-}" ]] && [[ -d "$dest/.git" ]]; then
    log "Reusing existing checkout: $dest"
    return
  fi
  rm -rf "$dest"
  log "Cloning $repo @ $ref"
  # Full history (not --depth 1): generators read git log for "last updated".
  git clone "https://github.com/$repo.git" "$dest"
  git -C "$dest" checkout "$ref"
}

build_core() {       # mdbook -> public/core
  local src="$1" out="$2"
  ( cd "$src/docs" && mdbook build -d "$out" )
}

build_python() {     # mkdocs-material -> public/python-sdk
  local src="$1" out="$2"
  ( cd "$src" && uv sync --group docs && uv run mkdocs build --site-dir "$out" )
}

build_node() {       # docusaurus (website/, baseUrl already /node-sdk/) -> public/node-sdk
  local src="$1" out="$2"
  ( cd "$src/website" && pnpm install --ignore-workspace && pnpm build )
  rm -rf "$out"; mkdir -p "$(dirname "$out")"
  cp -R "$src/website/build" "$out"
}

build_go() {         # hugo + hextra (website/) -> public/go-sdk
  local src="$1" out="$2"
  ( cd "$src/website" && hugo mod get github.com/imfing/hextra && hugo --gc --minify -b "/go-sdk/" -d "$out" )
}

# ---- hub mdBook at root FIRST ----
# mdBook cleans its -d target, so build the hub before the module subdirs are
# populated; the modules then land in subdirs the hub build won't touch.
log "Building hub mdBook -> public/ (root)"
( cd "$REPO_ROOT/docs" && mdbook build -d "$PUBLIC_DIR" )

# ---- per-module builds ----
COUNT="$(jq '.modules | length' "$REGISTRY")"
for i in $(seq 0 $((COUNT - 1))); do
  name="$(jq -r ".modules[$i].name"    "$REGISTRY")"
  repo="$(jq -r ".modules[$i].repo"    "$REGISTRY")"
  ref="$(jq -r  ".modules[$i].ref"     "$REGISTRY")"
  subpath="$(jq -r ".modules[$i].subpath" "$REGISTRY")"
  gen="$(jq -r  ".modules[$i].generator"  "$REGISTRY")"

  dest="$MODULES_DIR/$name"
  out="$PUBLIC_DIR/$subpath"

  clone_module "$repo" "$ref" "$dest"
  log "Building $name ($gen) -> public/$subpath/"
  case "$gen" in
    mdbook)          build_core   "$dest" "$out" ;;
    mkdocs-material) build_python "$dest" "$out" ;;
    docusaurus)      build_node   "$dest" "$out" ;;
    hugo-hextra)     build_go     "$dest" "$out" ;;
    *) fail "Unknown generator '$gen' for module '$name'" ;;
  esac
done

# ---- CNAME for the custom domain (owner attaches DNS) ----
echo "docs.agent-assembly.com" > "$PUBLIC_DIR/CNAME"

# ---- verification: every expected output dir must exist & be non-empty ----
log "Verifying aggregated output"
verify_nonempty() {
  local dir="$1" landing="$2"
  [[ -d "$dir" ]] || fail "Missing output dir: $dir"
  [[ -f "$dir/$landing" ]] || fail "Missing landing page: $dir/$landing"
  [[ -s "$dir/$landing" ]] || fail "Empty landing page: $dir/$landing"
  local n; n="$(find "$dir" -name '*.html' | wc -l | tr -d ' ')"
  [[ "$n" -ge 1 ]] || fail "No HTML files under $dir"
  printf '  ok  %-26s (%s html files)\n' "${dir#"$PUBLIC_DIR"/}" "$n"
}
verify_nonempty "$PUBLIC_DIR"            "index.html"
for sub in core python-sdk node-sdk go-sdk; do
  verify_nonempty "$PUBLIC_DIR/$sub"     "index.html"
done

# ---- unified search via Pagefind over the FINAL public/ ----
if [[ -z "${SKIP_PAGEFIND:-}" ]]; then
  log "Indexing public/ with Pagefind"
  npx -y pagefind --site "$PUBLIC_DIR"
  [[ -f "$PUBLIC_DIR/pagefind/pagefind.js" ]] || fail "Pagefind did not produce pagefind/pagefind.js"
  echo "  ok  pagefind index written"
fi

log "Aggregation complete -> $PUBLIC_DIR"
