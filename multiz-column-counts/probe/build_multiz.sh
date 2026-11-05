#!/usr/bin/env bash
# Build multiz from the v11.3 and v11.4 release tags with IDENTICAL flags, so any speed difference is the code.
# The upstream Makefile defaults to -O0, so both are built at -O2 here.
#
#   bash build_multiz.sh BUILD_DIR      # writes BUILD_DIR/multiz-v11.3 and BUILD_DIR/multiz-v11.4
set -euo pipefail
OUT=${1:?usage: build_multiz.sh BUILD_DIR}
FLAGS="-O2 -Wall -Wextra"
mkdir -p "$OUT"
for tag in v11.3 v11.4; do
  src="$OUT/src-$tag"
  [ -d "$src" ] || git -c advice.detachedHead=false clone -q --depth 1 --branch "$tag" https://github.com/multiz/multiz.git "$src"
  make -s -C "$src" multiz CFLAGS="$FLAGS" > "$OUT/build-$tag.log" 2>&1
  cp "$src/multiz" "$OUT/multiz-$tag"
  echo "$tag $(git -C "$src" rev-parse --short HEAD) $(gcc --version | head -1) flags: $FLAGS"
done
