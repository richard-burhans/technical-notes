#!/usr/bin/env python3
"""Time multiz v11.3 against v11.4 on synthetic block pairs of K and L rows, and check the outputs are identical.

    python3 run_sweep.py BUILD_DIR OUT_CSV [--sizes 2,4,8,16,32,64,128] [--reps 3]
    python3 run_sweep.py BUILD_DIR OUT_CSV --sizes 4x4,4x16,16x64 ...   # unequal depths K x L

BUILD_DIR holds multiz-v11.3 and multiz-v11.4 from build_multiz.sh. For each K = L in --sizes, make_blocks.py
writes a pair (10 blocks of 2,000 reference columns, seed 1), each release merges it --reps times, and the median
wall time is recorded. A size `KxL` gives unequal depths, a bare `K` means K = L. "identical" compares the two outputs with the `#` header lines removed.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import statistics
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent


def merge(binary: pathlib.Path, f1: pathlib.Path, f2: pathlib.Path, out: pathlib.Path) -> float:
    t0 = time.perf_counter()
    with out.open("w") as fh:
        subprocess.run([str(binary), str(f1), str(f2), "0"], stdout=fh, stderr=subprocess.DEVNULL, check=True)
    return time.perf_counter() - t0


def body(path: pathlib.Path) -> list[str]:
    return [ln for ln in path.read_text().splitlines() if not ln.startswith("#")]


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("build", type=pathlib.Path)
    ap.add_argument("out_csv", type=pathlib.Path)
    ap.add_argument("--sizes", default="2,4,8,16,32,64,128")
    ap.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    work = a.build / "sweep"
    work.mkdir(exist_ok=True)
    rows = []
    for size in a.sizes.split(","):
        k, l = (int(x) for x in size.split("x")) if "x" in size else (int(size), int(size))
        prefix = work / f"k{k}l{l}"
        subprocess.run([sys.executable, str(HERE / "make_blocks.py"), str(prefix), str(k), str(l)], check=True)
        f1, f2 = pathlib.Path(f"{prefix}.1.maf"), pathlib.Path(f"{prefix}.2.maf")
        t = {}
        for v in ("v11.3", "v11.4"):
            t[v] = statistics.median(merge(a.build / f"multiz-{v}", f1, f2, work / f"k{k}l{l}.{v}.out")
                                     for _ in range(a.reps))
        same = body(work / f"k{k}l{l}.v11.3.out") == body(work / f"k{k}l{l}.v11.4.out")
        rows.append({"K": k, "L": l, "KxL": k * l, "KplusL": k + l, "v11.3_s": f"{t['v11.3']:.3f}",
                     "v11.4_s": f"{t['v11.4']:.3f}", "speedup": f"{t['v11.3'] / t['v11.4']:.2f}",
                     "identical": same})
        print(rows[-1], flush=True)
    with a.out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return 0 if all(r["identical"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
