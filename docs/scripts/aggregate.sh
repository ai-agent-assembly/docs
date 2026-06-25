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

build_core() {       # mdbook -> /core/{latest,<tag>...}/ + full versions.json + redirect (AAASM-3753)
  # The core docs ship a channel-based version selector (docs/theme/index.hbs
  # #aaasm-version-selector) that reads /core/versions.json at runtime and
  # navigates to /core/<channel-or-tag>/. To list the FULL archived version set
  # in the hub (not just `latest`), reproduce the core docs.yml deploy exactly:
  #   /core/latest/         book built from master HEAD (default channel)
  #   /core/<vX.Y.Z[-pre]>/  frozen book rebuilt from EACH release git tag
  #   /core/versions.json   manifest (channels + archived[]) via docs/ci/build_versions.py
  #   /core/index.html      site-root redirect (stable -> pre-release -> latest)
  # git is the source of truth (AAASM-2827): the core deploy rebuilds every tag's
  # book from git on each run, so the hub does the same rather than mirroring the
  # (lossy) live Pages site. A tag with no docs/book.toml or a failing build is
  # logged and skipped (its subpath is simply absent) — never fatal, matching
  # docs.yml.
  local src="$1" out="$2"
  mkdir -p "$out/latest"
  ( cd "$src/docs" && mdbook build -d "$out/latest" )

  # Rebuild every release tag's book into /core/<tag>/ (one worktree per tag,
  # torn down after). extra-archived.txt feeds build_versions.py's archived[].
  : > "$src/extra-archived.txt"
  local tag workdir
  while IFS= read -r tag; do
    [[ -z "$tag" ]] && continue
    workdir="$(mktemp -d)"
    if git -C "$src" worktree add --detach "$workdir" "$tag" >/dev/null 2>&1 \
       && [[ -f "$workdir/docs/book.toml" ]] \
       && ( cd "$workdir/docs" && mdbook build -d "$out/$tag" ) >/dev/null 2>&1; then
      echo "$tag" >> "$src/extra-archived.txt"
      printf '  built core archived %s\n' "$tag"
    else
      printf '  WARN skipping core tag %s (no docs/book.toml or build failed)\n' "$tag"
    fi
    git -C "$src" worktree remove --force "$workdir" >/dev/null 2>&1 || true
    rm -rf "$workdir"
  done < <(git -C "$src" tag --list 'v[0-9]*.[0-9]*.[0-9]*' | sort)

  # Manifest: reuse the repo's own channel computation (docs/ci/build_versions.py).
  # archived[] is seeded from the rebuilt tags (extra-archived.txt) so it is
  # self-healing from git; the moving pre-release/stable channel pointers are
  # seeded from the live deployed manifest (the only place those persist — and a
  # missing fetch only drops the moving channels, never archived[]). This is what
  # docs.yml does on a master-push cut.
  ( cd "$src"
    curl -fsSL "https://ai-agent-assembly.github.io/agent-assembly/versions.json" \
      -o prior-versions.json 2>/dev/null || rm -f prior-versions.json
    python3 docs/ci/build_versions.py latest latest "$out/versions.json" )

  cp "$src/docs/site-root-index.html" "$out/index.html"
}

build_python() {     # mike-published version tree (gh-pages) -> public/python-sdk (AAASM-3752)
  # The python-sdk publishes its FULL mkdocs+mike version tree (versions.json,
  # per-version dirs, and channel aliases latest/stable/pre-release) to its
  # gh-pages branch. A plain `mkdocs build` drops versions.json and every
  # version dir, so the mike version dropdown 404s. Reuse the already-published
  # gh-pages tree verbatim — its layout (gh-pages root == /python-sdk/) is the
  # exact layout the standalone site serves, so the switcher works unchanged.
  local out="$1" repo="$2"
  local ghp="$MODULES_DIR/python-sdk-ghpages"
  rm -rf "$ghp"
  log "Cloning $repo @ gh-pages (mike version tree)"
  git clone --depth 1 -b gh-pages "https://github.com/$repo.git" "$ghp"
  rm -rf "$out"; mkdir -p "$out"
  # cp -RL dereferences mike's alias symlinks (latest/stable/pre-release) into
  # real directories — GitHub Pages does not follow symlinks.
  cp -RL "$ghp/." "$out/"
  rm -rf "$out/.git"
}

build_node() {       # docusaurus (website/, baseUrl already /node-sdk/) -> public/node-sdk
  local src="$1" out="$2"
  ( cd "$src/website" && pnpm install --ignore-workspace && pnpm build )
  rm -rf "$out"; mkdir -p "$(dirname "$out")"
  cp -R "$src/website/build" "$out"
}

build_go() {         # hugo + hextra FULL version tree (every git tag) -> public/go-sdk (AAASM-3753)
  # The go-sdk version selector is BAKED INTO each page at Hugo build time from
  # website/data/versions.toml (params.versionsBasePath /go-sdk). The committed
  # versions.toml lists only `latest`; the archived tag entries + moving
  # pre-release/stable channels are recomputed from git tags by the release job
  # (docs-site.yml). To list the FULL archived set in the hub we replicate that
  # recompute step BEFORE running the repo's build_all_versions.sh, which then
  # materialises /go-sdk/<tag>/ for every archived entry (plus the channels).
  # git tags are the source of truth; we never mirror the (lossy) live Pages site.
  local src="$1" out="$2"

  # 1. Recompute versions.toml from git tags (verbatim replica of docs-site.yml's
  #    "Recompute versions.toml from git tags" step — reuses the repo's own
  #    website/scripts/versions_channels.py so the channel logic cannot drift).
  local tags
  tags="$(git -C "$src" tag -l 'v*' | tr '\n' ' ')"
  # shellcheck disable=SC2086 # tags are simple vX.Y.Z[-pre] refs; word-split intended
  ( cd "$src" && python3 - website/data/versions.toml $tags <<'PY'
import os, re, sys
sys.path.insert(0, os.path.join("website", "scripts"))
from versions_channels import compute_channels, parse_tag  # noqa: E402

path = sys.argv[1]
raw_tags = sys.argv[2:]
with open(path, encoding="utf-8") as fh:
    text = fh.read()
blocks = re.split(r'(?m)^\[\[versions\]\]\s*$', text)
head = blocks[0]
existing = []
for body in blocks[1:]:
    fields = dict(re.findall(r'(\w+)\s*=\s*"([^"]+)"', body))
    flags = dict(re.findall(r'(\w+)\s*=\s*(true|false)\b', body))
    fields.update({k: v for k, v in flags.items()})
    existing.append(fields)
latest = [r for r in existing if r.get("channel") == "latest"]
if not latest:
    latest = [{"channel": "latest", "version": "latest",
               "label": "latest (master)", "path": "/latest/", "default": "true"}]
tag_set = {t for t in raw_tags if t and parse_tag(t) is not None}
channels = compute_channels(sorted(tag_set))
archived = []
for tag in sorted(tag_set, key=lambda t: parse_tag(t).raw if parse_tag(t) else t):
    archived.append({"channel": "archived", "version": tag, "label": tag, "path": f"/{tag}/"})

def emit(r):
    order = ["channel", "version", "label", "path", "tag", "default"]
    keys = order + [k for k in r if k not in order]
    lines = ["[[versions]]"]
    for k in keys:
        if k not in r:
            continue
        v = r[k]
        lines.append(f"  {k} = {v}" if v in ("true", "false") else f'  {k} = "{v}"')
    return "\n".join(lines)

out_records = list(latest)
for channel in ("stable", "pre-release"):
    tag = channels.get(channel)
    if tag:
        out_records.append({"channel": channel, "version": channel,
                            "label": f"{channel} ({tag})", "path": f"/{channel}/", "tag": tag})
out_records.extend(archived)
out = head.rstrip("\n") + "\n" + "\n" + "\n\n".join(emit(r) for r in out_records) + "\n"
with open(path, "w", encoding="utf-8") as fh:
    fh.write(out)
print(f"Recomputed {len(tag_set)} archived go-sdk tag(s); channels={channels}")
PY
  )

  # 2. Build every subpath now listed in versions.toml (latest + channels + every
  #    archived tag). build_all_versions.sh overlays the recomputed versions.toml
  #    into each historical worktree so every snapshot's selector lists the full set.
  ( cd "$src" \
    && PAGES_BASE="/go-sdk" PUBLIC_DIR="$out" REPO_ROOT="$src" MASTER_REF="HEAD" \
       bash website/scripts/build_all_versions.sh )
  # Site-root redirect (stable -> pre-release -> latest) so /go-sdk/ resolves.
  local default_path
  default_path="$(python3 - "$src/website/data/versions.toml" <<'PY'
import sys, re
text = open(sys.argv[1], encoding="utf-8").read()
paths = {}
for body in re.split(r'(?m)^\[\[versions\]\]\s*$', text)[1:]:
    ch = re.search(r'channel\s*=\s*"([^"]+)"', body)
    pa = re.search(r'path\s*=\s*"([^"]+)"', body)
    if ch and pa:
        paths[ch.group(1)] = pa.group(1)
for channel in ("stable", "pre-release", "latest"):
    if channel in paths:
        print("." + paths[channel]); break
else:
    print("./latest/")
PY
)"
  sed "s#@@DEFAULT_PATH@@#${default_path}#g" "$src/website/redirect/index.html" > "$out/index.html"
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

  # python-sdk reuses its published gh-pages tree (no source build needed), so
  # skip the master checkout for it; every other module builds from source.
  if [[ "$gen" != "mkdocs-material" ]]; then
    clone_module "$repo" "$ref" "$dest"
  fi
  log "Building $name ($gen) -> public/$subpath/"
  case "$gen" in
    mdbook)          build_core   "$dest" "$out" ;;
    mkdocs-material) build_python "$out" "$repo" ;;
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

# ---- version-switcher machinery must be present (AAASM-3752) ----
# Each module's per-version switcher needs its manifest + the subpath(s) it
# references. Assert them so a regression that drops the version tree fails the
# build instead of silently shipping 404ing dropdowns.
verify_manifest() {
  local f="$1"
  [[ -s "$f" ]] || fail "Missing/empty version manifest: ${f#"$PUBLIC_DIR"/}"
  printf '  ok  %-26s (version manifest)\n' "${f#"$PUBLIC_DIR"/}"
}
verify_manifest "$PUBLIC_DIR/python-sdk/versions.json"
verify_manifest "$PUBLIC_DIR/core/versions.json"
verify_nonempty "$PUBLIC_DIR/core/latest"     "index.html"
verify_nonempty "$PUBLIC_DIR/go-sdk/latest"   "index.html"

# ---- unified search via Pagefind over the FINAL public/ ----
if [[ -z "${SKIP_PAGEFIND:-}" ]]; then
  log "Indexing public/ with Pagefind"
  npx -y pagefind --site "$PUBLIC_DIR"
  [[ -f "$PUBLIC_DIR/pagefind/pagefind.js" ]] || fail "Pagefind did not produce pagefind/pagefind.js"
  echo "  ok  pagefind index written"
fi

log "Aggregation complete -> $PUBLIC_DIR"
