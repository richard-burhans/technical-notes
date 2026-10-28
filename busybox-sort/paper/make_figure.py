#!/usr/bin/env python3
"""Figure 1: BusyBox sort's peak memory per input line, against line length, with the sizing budget.

    uv run --with matplotlib make_figure.py

Reads ../measurements/line_length_sweep.csv (written by ../probe/probe_container.py --sweep) and writes
figure1.pdf next to this script.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "measurements" / "line_length_sweep.csv"
# Okabe-Ito
BLUE, ORANGE, GREY = "#0072B2", "#E69F00", "#7f7f7f"


def main() -> None:
    rows = list(csv.DictReader(CSV.open()))
    length = [int(r["line_bytes"]) for r in rows]
    lines = [int(r["lines"]) for r in rows]
    size = [int(r["input_bytes"]) for r in rows]
    peak = [int(r["peak_bytes"]) for r in rows]
    base = [int(r["empty_container_peak_bytes"]) for r in rows]
    per_line = [(p - b) / n for p, b, n in zip(peak, base, lines, strict=True)]
    budget = [(2.5 * s + 40 * n) / n for s, n in zip(size, lines, strict=True)]

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=(85 / 25.4, 62 / 25.4))
    ax.plot(length, length, color=GREY, lw=0.8, ls=":", label="the line itself")
    ax.plot(
        length, budget, color=ORANGE, lw=1.0, ls="--", label="budget: 2.5 × line + 40 B"
    )
    ax.plot(length, per_line, color=BLUE, lw=1.2, marker="o", ms=2.5, label="measured")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ticks = [8, 16, 32, 64, 128, 256, 512, 1024]
    ax.set_xticks(ticks, [str(t) for t in ticks])
    ax.set_yticks(
        [8, 16, 32, 64, 128, 256, 512, 1024, 2048],
        ["8", "16", "32", "64", "128", "256", "512", "1024", "2048"],
    )
    ax.set_xlabel("line length, newline included (bytes)", fontsize=8)
    ax.set_ylabel("peak memory per input line (bytes)", fontsize=8)
    ax.axvspan(120, 256, color=BLUE, alpha=0.08, lw=0)
    ax.text(175, 22, "120–256 B lines:\n~275 B each", ha="center", fontsize=6, color=BLUE)
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    fig.tight_layout()
    out = HERE / "figure1.pdf"
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
