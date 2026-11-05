#!/usr/bin/env python3
"""Figure 2: multiz v11.3 against v11.4 wall time as block depth grows, from ../measurements/sweep.csv.

    uv run --no-project --with matplotlib python make_figure2.py
"""
import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
rows = list(csv.DictReader((HERE / "../measurements/sweep.csv").open()))
k = [int(r["K"]) for r in rows]
t3 = [float(r["v11.3_s"]) for r in rows]
t4 = [float(r["v11.4_s"]) for r in rows]
assert all(r["identical"] == "True" for r in rows), "an output differed"

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
                     "font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(3.35, 2.6))
ax.loglog(k, t3, "o-", color="#D55E00", label="v11.3: every row pair", ms=4)
ax.loglog(k, t4, "s-", color="#009E73", label="v11.4: column counts", ms=4)
ref = [t3[-1] * (x / k[-1]) ** 2 for x in k]           # slope 2 guide through the last v11.3 point
ax.loglog(k, ref, ":", color="#7F7F7F", lw=0.8, label="∝ K × L (slope 2)")
ax.set_xlabel("rows per block, K = L")
ax.set_ylabel("wall time (s)")
ax.set_xticks(k)
ax.set_xticklabels([str(x) for x in k])
ax.minorticks_off()
for r, x, a, b in zip(rows, k, t3, t4):              # the label is the CSV's own speedup column
    if x in (8, 32, 128):
        left = x == k[-1]
        ax.annotate(f"{float(r['speedup']):.0f}×", (x, (a * b) ** 0.5), ha="right" if left else "left",
                    va="center", fontsize=7, xytext=(-4 if left else 3, 0), textcoords="offset points")
ax.legend(frameon=False, fontsize=7, loc="upper left")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(HERE / f"figure2.{ext}", dpi=300)
print("wrote figure2.pdf and figure2.png")
