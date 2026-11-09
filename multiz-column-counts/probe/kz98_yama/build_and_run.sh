#!/usr/bin/env bash
# Build the yama harness against multiz releases v11.4 and v11.9, then compare yama's gap charges and
# output with Kececioglu and Zhang (1998) eqs. (42)-(44). See measurements/kz98_yama_gap_terms.md.
#
# Usage: build_and_run.sh WORKDIR [SEED]   (WORKDIR receives the multiz sources and the two binaries)
set -euo pipefail
W=$(realpath -m "$1"); SEED=${2:-7}
HERE=$(dirname "$(realpath "$0")")
mkdir -p "$W"
# Tags are pinned to the commits this check was run against; a moved tag fails here rather than silently.
declare -A SHA=([v11.4]=6bfe6a4771254e2639882c0f9d8a0f8a86172afb [v11.9]=077e8479af2478f747d9e0e1243702a2822d2a59)
for v in v11.4 v11.9; do
  [ -d "$W/$v" ] || git clone -q --depth 1 --branch "$v" https://github.com/multiz/multiz.git "$W/$v"
  [ "$(git -C "$W/$v" rev-parse HEAD)" = "${SHA[$v]}" ] || { echo "$v is not ${SHA[$v]}" >&2; exit 1; }
  gcc -O2 -I"$W/$v" "$HERE/main.c" "$W/$v/mz_yama.c" "$W/$v/mz_scores.c" "$W/$v/util.c" -o "$W/yama_$v"
done
python3 "$HERE/kz_vs_yama.py" "$SEED" 1000 "$W/yama_v11.4" "$W/yama_v11.9"
