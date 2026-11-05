#!/usr/bin/env python3
"""Figure 3: v11.3 time against K x L and v11.4 time against K + L, over equal and unequal depths.

    uv run --no-project --with matplotlib python make_figure3.py

Reads ../measurements/sweep.csv (K = L) and ../measurements/grid.csv (K, L in {4, 16, 64}).
"""
import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
M = HERE / "../measurements"
sweep = list(csv.DictReader((M / "sweep.csv").open()))
grid = list(csv.DictReader((M / "grid.csv").open()))
assert all(r["identical"] == "True" for r in sweep + grid), "an output differed"

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
                     "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
fig, (a, b) = plt.subplots(1, 2, figsize=(6.7, 2.7))
for ax, xkey, ykey, col, lab in ((a, "KxL", "v11.3_s", "#D55E00", "v11.3 against K × L"),
                                 (b, "KplusL", "v11.4_s", "#009E73", "v11.4 against K + L")):
    for rows, mk, name in ((sweep, "o", "K = L"), (grid, "^", "K ≠ L grid")):
        xs = [int(r[xkey]) for r in rows if name == "K = L" or r["K"] != r["L"]]
        ys = [float(r[ykey]) for r in rows if name == "K = L" or r["K"] != r["L"]]
        ax.loglog(xs, ys, mk, color=col, ms=4.5 if mk == "o" else 5.5, mfc=col if mk == "o" else "white",
                  label=name)
    ax.set_ylabel(f"{ykey.split('_')[0]} wall time (s)")
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.minorticks_off()
a.set_xlabel("K × L (row pairs per cell)")
b.set_xlabel("K + L (rows counted per column pair)")
xs = [int(r["KxL"]) for r in sweep]
t_ref = float(sweep[-1]["v11.3_s"]) / int(sweep[-1]["KxL"])
a.loglog(xs, [t_ref * x for x in xs], ":", color="#7F7F7F", lw=0.8)
a.text(0.97, 0.05, "dotted: slope 1", transform=a.transAxes, ha="right", fontsize=7, color="#555555")
a.text(-0.16, 1.04, "A", transform=a.transAxes, fontsize=11, fontweight="bold")
b.text(-0.16, 1.04, "B", transform=b.transAxes, fontsize=11, fontweight="bold")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(HERE / f"figure3.{ext}", dpi=300)
print("wrote figure3.pdf and figure3.png")
