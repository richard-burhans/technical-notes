#!/usr/bin/env bash
# gprof flat profiles of multiz v11.3 and v11.4 on the K = L = 128 sweep pair, built -O2 -pg from the release tags.
#
#   bash profile_k128.sh BUILD_DIR > ../measurements/gprof_k128.txt
# Needs build_multiz.sh and run_sweep.py to have run with BUILD_DIR first (sources and the k128 pair).
set -euo pipefail
B=${1:?usage: profile_k128.sh BUILD_DIR}
echo "# gprof flat profiles, multiz built -O2 -pg from the v11.3 and v11.4 tags, merging the K = L = 128 sweep pair (seed 1)"
for tag in v11.3 v11.4; do
  rm -rf "$B/prof-$tag" && cp -r "$B/src-$tag" "$B/prof-$tag"
  make -s -C "$B/prof-$tag" clean > /dev/null 2>&1 || true
  make -s -C "$B/prof-$tag" multiz CFLAGS="-O2 -pg" > /dev/null 2>&1
  (cd "$B/prof-$tag" && ./multiz ../sweep/k128.1.maf ../sweep/k128.2.maf 0 > /dev/null 2>&1)
  echo "## $tag"
  gprof -b -p "$B/prof-$tag/multiz" "$B/prof-$tag/gmon.out" | sed -n 1,12p
  echo
done
