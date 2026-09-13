#!/usr/bin/env bash
set -euo pipefail

# Exercise the real aggregate.sh scope/restore functions against a tiny mike
# fixture, without cloning every module or running the aggregate build.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixture_root="$(mktemp -d)"
trap 'rm -rf "$fixture_root"' EXIT
PUBLIC_DIR="$fixture_root/public"
MODULES_DIR="$fixture_root/modules"
PF_HOLD="$MODULES_DIR/.pagefind-hold"
PF_HOLD_LANG="$MODULES_DIR/.pagefind-hold-lang"
HUB_LANGUAGES=(zh-Hant)

mkdir -p "$PUBLIC_DIR/zh-Hant" "$MODULES_DIR"
mkdir -p "$PUBLIC_DIR/core/latest"
printf '%s\n' 'Hub combined print view' > "$PUBLIC_DIR/print.html"
printf '%s\n' 'Core combined print view' > "$PUBLIC_DIR/core/latest/print.html"
mkdir -p "$MODULES_DIR/node-sdk/website" "$PUBLIC_DIR/node-sdk/examples/mastra" \
  "$PUBLIC_DIR/node-sdk/next/examples/mastra" \
  "$PUBLIC_DIR/node-sdk/0.0.1-rc.4/examples/mastra" \
  "$PUBLIC_DIR/node-sdk/0.0.1-beta.1/examples/mastra"
printf '%s\n' '["0.0.1-rc.4","0.0.1-beta.1"]' > "$MODULES_DIR/node-sdk/website/versions.json"
printf '%s\n' '{"lastVersion":"0.0.1-rc.4","versions":{"current":{"path":"/next/"}}}' \
  > "$MODULES_DIR/node-sdk/website/versionChannels.json"
for channel in root next 0.0.1-rc.4 0.0.1-beta.1; do
  target="$PUBLIC_DIR/node-sdk/$channel/examples/mastra/index.html"
  if [[ "$channel" == root ]]; then target="$PUBLIC_DIR/node-sdk/examples/mastra/index.html"; fi
  printf '%s\n' "node-sdk/$channel Mastra" > "$target"
done
for module in python-sdk arena; do
  mkdir -p "$PUBLIC_DIR/$module/latest" "$PUBLIC_DIR/$module/v0.0.1" "$PUBLIC_DIR/$module/pre-release"
  printf '%s\n' '[{"version":"v0.0.1","aliases":["latest","pre-release"]}]' > "$PUBLIC_DIR/$module/versions.json"
  for channel in latest v0.0.1 pre-release; do
    printf '%s\n' "$module/$channel" > "$PUBLIC_DIR/$module/$channel/index.html"
  done
done

# Function boundaries in aggregate.sh are top-level; source only these two
# definitions so this test never starts the costly module aggregation.
eval "$(sed -n '/^scope_pagefind() {/,/^}/p; /^restore_pagefind() {/,/^}/p' "$script_dir/aggregate.sh")"
declare -F scope_pagefind restore_pagefind >/dev/null

scope_pagefind
[[ -f "$PUBLIC_DIR/print.html" ]]
[[ -f "$PUBLIC_DIR/core/latest/print.html" ]]
[[ -f "$PUBLIC_DIR/node-sdk/examples/mastra/index.html" ]]
for channel in next 0.0.1-rc.4 0.0.1-beta.1; do
  [[ ! -e "$PUBLIC_DIR/node-sdk/$channel" ]]
  [[ -f "$PF_HOLD/node-sdk__$channel/examples/mastra/index.html" ]]
done
for module in python-sdk arena; do
  [[ -f "$PUBLIC_DIR/$module/latest/index.html" ]]
  [[ ! -e "$PUBLIC_DIR/$module/v0.0.1" ]]
  [[ ! -e "$PUBLIC_DIR/$module/pre-release" ]]
  [[ -f "$PF_HOLD/${module}__v0.0.1/index.html" ]]
  [[ -f "$PF_HOLD/${module}__pre-release/index.html" ]]
done
[[ ! -e "$PUBLIC_DIR/zh-Hant" ]]
[[ -d "$PF_HOLD_LANG/zh-Hant" ]]

restore_pagefind
restore_pagefind # idempotent, as required by the aggregate EXIT trap
[[ -f "$PUBLIC_DIR/print.html" ]]
[[ -f "$PUBLIC_DIR/core/latest/print.html" ]]
[[ -f "$PUBLIC_DIR/node-sdk/examples/mastra/index.html" ]]
for channel in next 0.0.1-rc.4 0.0.1-beta.1; do
  [[ -f "$PUBLIC_DIR/node-sdk/$channel/examples/mastra/index.html" ]]
done
for module in python-sdk arena; do
  for channel in latest v0.0.1 pre-release; do
    [[ -f "$PUBLIC_DIR/$module/$channel/index.html" ]]
  done
done
[[ -d "$PUBLIC_DIR/zh-Hant" ]]
[[ ! -e "$PF_HOLD" ]]
[[ ! -e "$PF_HOLD_LANG" ]]
printf '%s\n' 'PASS: default-channel search scope and full archive restoration (node-sdk, python-sdk, arena, localized hub)'
