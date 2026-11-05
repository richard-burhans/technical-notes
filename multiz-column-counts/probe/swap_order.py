#!/usr/bin/env python3
"""Does argument order change multiz v11.3's time on the SAME pair of files? Swap them and time both orders.

    python3 swap_order.py BUILD_DIR OUT_CSV [--pairs 4x16,4x64] [--reps 5]

For each pair KxL from the grid (BUILD_DIR/sweep/k{K}l{L}.1.maf and .2.maf, written by run_sweep.py), v11.3 merges
file 1 with file 2 and then file 2 with file 1, alternating, --reps times each. The file contents are identical in
both orders, so any difference is the order. Records the median wall time of each order.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import statistics
import subprocess
import sys
import time


def merge(binary: pathlib.Path, f1: pathlib.Path, f2: pathlib.Path) -> float:
    t0 = time.perf_counter()
    subprocess.run([str(binary), str(f1), str(f2), "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   check=True)
    return time.perf_counter() - t0


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("build", type=pathlib.Path)
    ap.add_argument("out_csv", type=pathlib.Path)
    ap.add_argument("--pairs", default="4x16,4x64")
    ap.add_argument("--reps", type=int, default=5)
    a = ap.parse_args()
    binary = a.build / "multiz-v11.3"
    rows = []
    for pair in a.pairs.split(","):
        k, l = (int(x) for x in pair.split("x"))
        f1 = a.build / "sweep" / f"k{k}l{l}.1.maf"      # K rows
        f2 = a.build / "sweep" / f"k{k}l{l}.2.maf"      # L rows
        shallow_first, deep_first = [], []
        for _ in range(a.reps):                          # alternate the orders so load drifts hit both
            shallow_first.append(merge(binary, f1, f2))
            deep_first.append(merge(binary, f2, f1))
        s, d = statistics.median(shallow_first), statistics.median(deep_first)
        rows.append({"pair": f"{k}x{l}", "KxL": k * l, "shallow_first_s": f"{s:.3f}", "deep_first_s": f"{d:.3f}",
                     "deep_first_extra_pct": f"{100 * (d / s - 1):.1f}",
                     "shallow_first_range_s": f"{min(shallow_first):.3f}-{max(shallow_first):.3f}",
                     "deep_first_range_s": f"{min(deep_first):.3f}-{max(deep_first):.3f}"})
        print(rows[-1], flush=True)
    with a.out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
