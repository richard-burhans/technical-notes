#!/usr/bin/env bash
# gprof profile of a whole roast with multiz v11.4. roast and maf_project are the ordinary -O2 release build. multiz
# is built -O2 -pg and reached through a wrapper that sets GMON_OUT_PREFIX, so each multiz process (one per merge)
# writes its own gmon file and no other program writes one. The files are then summed with gprof -s.
#
#   bash profile_wholepiece.sh BUILD_DIR INPUT_DIR TREE_FILE REF > gprof_wholepiece_rerun.txt
#
# INPUT_DIR holds the pairwise REF.*.sing.maf inputs of one piece and TREE_FILE the roast guide tree. For the
# measured piece (cs10 NC_044376.1, piece 02, 216 assemblies, REF cs10_NCBI_RefSeq_softmasked) the inputs are listed
# with checksums in ../measurements/wholepiece_inputs.sha256 and the tree is ../measurements/wholepiece_tree.txt.
# Needs build_multiz.sh to have run with BUILD_DIR first.
# The committed profiles were made by two runs that built every program -pg and summed the 215 gmon files written by
# multiz, one per merge. This script profiles only multiz, which should give the same multiz samples, but it has not itself been run.
set -euo pipefail
B=$(realpath "${1:?usage}"); IN=$(realpath "${2:?usage}"); TREE=$(realpath "${3:?usage}"); REF=${4:?usage}
R="$B/rel-wholepiece"; P="$B/prof-wholepiece"; W="$B/run-wholepiece"
rm -rf "$R" "$P" "$W" && cp -r "$B/src-v11.4" "$R" && cp -r "$B/src-v11.4" "$P"
make -s -C "$R" clean > /dev/null 2>&1 || true; make -s -C "$R" CFLAGS="-O2" > /dev/null 2>&1
make -s -C "$P" clean > /dev/null 2>&1 || true; make -s -C "$P" multiz CFLAGS="-O2 -pg" > /dev/null 2>&1
mkdir -p "$W/bin" "$W/tmp" "$W/gmon"
printf '#!/bin/sh\nGMON_OUT_PREFIX=%s/gmon/gmon exec %s/multiz "$@"\n' "$W" "$P" > "$W/bin/multiz"
chmod +x "$W/bin/multiz"
ln -s "$IN"/"$REF".*.sing.maf "$W"/
cd "$W"
PATH="$W/bin:$R:$PATH" roast + T="$W/tmp" E="$REF" "$(cat "$TREE")" "$REF".*.sing.maf out.maf > /dev/null 2> roast.err
set -- gmon/gmon.*
echo "# gprof, multiz v11.4 -O2 -pg, summed over $# multiz processes of one roast"
gprof -s "$P/multiz" "$@" && gprof -b -p "$P/multiz" gmon.sum | sed -n 1,20p
