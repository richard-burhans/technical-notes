#!/usr/bin/env python3
"""Explainer figure for MULTIZ 11.4's column-count dynamic programming (`multiz#28`): K x L becomes K + L.

    python3 make_figure1.py

Writes `figure1.svg` and `.pdf` beside this script (PDF by rsvg-convert). The figure shows K x L work per cell becoming
K + L work per column. Thanks to Minmei Hou for discussion.

Design rules (writing repo, papers/rules/figure_design.md): 510 pt canvas = 180 mm, Okabe-Ito colours,
Helvetica throughout (panel letters 11 pt, titles 8 pt, labels 6.5 to 7 pt), zero baseline on the bar panel.

Panels A and B are a toy column pair (K = 5, L = 4), drawn to show the counting, not measured. Panel C's numbers
are the ones `multiz#28` records, as named constants below.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).parent
W, H = 510, 330
FONT = 'font-family="Helvetica,Arial,sans-serif"'
BLUE, ORANGE, GREEN, VERMILION, GREY, INK = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#9A9A9A", "#000000"
BLUE_T, ORANGE_T, GREEN_T = "#CCE3F0", "#FAECCC", "#CCECE3"   # ~20% tints on white (rsvg has no opacity issue)

# multiz#28 (merged 2026-10-21), "Measured": one deep merge from a 216-genome roast, single upstream runs.
MERGE_BLOCKS_A, MERGE_ROWS_A = 2303, 35      # "2,303 blocks of ~35 rows"
MERGE_BLOCKS_B, MERGE_ROWS_B = 4359, 43      # "against 4,359 of ~43"
MERGE_S_113, MERGE_S_114 = 981, 29           # "981 s -> 29 s against the 11.3 release build"

COL_A = ["A", "A", "G", "A", "-"]            # toy column of alignment A, K = 5 rows
COL_B = ["A", "G", "G", "A"]                 # toy column of alignment B, L = 4 rows

el: list[str] = []


def text(x, y, s, size=7.0, anchor="start", weight="normal", fill=INK, style=""):
    st = f' font-style="{style}"' if style else ""
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
              f'font-weight="{weight}" fill="{fill}"{st}>{s}</text>')


def rect(x, y, w, h, fill, stroke="none"):
    el.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
              f'stroke="{stroke}" stroke-width="0.6"/>')


def line(x1, y1, x2, y2, stroke=GREY, width=0.6, marker=False):
    m = ' marker-end="url(#arrow)"' if marker else ""
    el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
              f'stroke-width="{width}"{m}/>')


def column(x, y0, letters, fill, tint, cell=16):
    """A stacked alignment column. Returns the centre y of each row."""
    ys = []
    for i, s in enumerate(letters):
        y = y0 + i * cell
        rect(x, y, cell, cell - 2, tint, fill)
        text(x + cell / 2, y + cell / 2 + 2.3, s, 7.5, "middle", "bold", fill)
        ys.append(y + (cell - 2) / 2)
    return ys


# ---- headline -------------------------------------------------------------------------------------------------
text(8, 14, "MULTIZ 11.4 scores each yama cell from column counts, not K × L row pairs", 9, weight="bold")

# ---- A: release 11.3, every row pair -------------------------------------------------------------------------
text(8, 36, "A", 11, weight="bold")
text(22, 36, "11.3: every row pair, in every cell", 8, weight="bold")
ax, bx, y0 = 40, 190, 58
ya = column(ax, y0, COL_A, BLUE, BLUE_T)
yb = column(bx, y0 + 8, COL_B, ORANGE, ORANGE_T)
for y1 in ya:
    for y2 in yb:
        line(ax + 16, y1, bx, y2, GREY, 0.5)
text(ax + 8, y0 - 6, "column of A", 6.5, "middle", fill=BLUE)
text(ax + 8, y0 + 90, "K = 5 rows", 6.5, "middle", fill=BLUE)
text(bx + 8, y0 + 2, "column of B", 6.5, "middle", fill=ORANGE)
text(bx + 8, y0 + 82, "L = 4 rows", 6.5, "middle", fill=ORANGE)
text(123, 172, "K × L = 20 pair scores", 8, "middle", "bold", VERMILION)
text(123, 183, "for every DP cell, four times over", 6.5, "middle")
text(123, 192, "(the substitution sum and three gap sums)", 6.5, "middle")

# ---- B: release 11.4, count once per column, combine per cell -------------------------------------------------
X = 262
text(X - 8, 36, "B", 11, weight="bold")
text(X + 6, 36, "11.4: summarise each column once, then combine", 8, weight="bold")
column(X + 4, y0, COL_A, BLUE, BLUE_T, cell=13)
column(X + 4, y0 + 74, COL_B, ORANGE, ORANGE_T, cell=13)
vx = X + 44
# A folded into a weight vector: one score per symbol of B
line(X + 19, y0 + 31, vx - 3, y0 + 31, INK, 0.7, marker=True)
text(vx, y0 + 12, "fold A: one score per symbol", 6.5)
for i, s in enumerate(["A", "C", "G", "T"]):
    rect(vx + i * 22, y0 + 20, 20, 20, BLUE_T, BLUE)
    text(vx + i * 22 + 10, y0 + 33, f"w({s})", 6, "middle")
text(vx, y0 + 52, "K per symbol, per column of A", 6.5, fill=BLUE, weight="bold")
# B reduced to counts
line(X + 19, y0 + 99, vx - 3, y0 + 99, INK, 0.7, marker=True)
text(vx, y0 + 80, "count B's symbols (dash too)", 6.5)
for i, (s, n) in enumerate([("A", 2), ("C", 0), ("G", 2), ("T", 0)]):
    rect(vx + i * 22, y0 + 88, 20, 20, ORANGE_T, ORANGE)
    text(vx + i * 22 + 10, y0 + 101, f"{s}:{n}", 6, "middle")
text(vx, y0 + 120, "L work, per column of B", 6.5, fill="#9C6A00", weight="bold")
# the cell
cx = X + 150
line(vx + 90, y0 + 31, cx, y0 + 58, INK, 0.7, marker=True)
line(vx + 90, y0 + 99, cx, y0 + 74, INK, 0.7, marker=True)
rect(cx + 2, y0 + 52, 92, 28, GREEN_T, GREEN)
text(cx + 48, y0 + 64, "2·w(A) + 2·w(G)", 7.5, "middle", "bold", GREEN)
text(cx + 48, y0 + 74, "the DP cell", 6, "middle")
text(cx + 48, 172, "K + L = 9 rows", 8, "middle", "bold", GREEN)
text(cx + 48, 183, "summarised once per column", 6.5, "middle")
text(cx + 48, 192, "then a short dot product per cell", 6.5, "middle")

# ---- the gap sums, which tie A and B together ------------------------------------------------------------------
rect(8, 204, 494, 30, "#F2F2F2")
text(16, 216, "Gap sums are counted the same way. A row's gap cost depends only on whether it holds a dash in this column", 6.5)
text(16, 226, "and in the previous one, so each row falls into one of 4 dash classes. All terms are integers: the totals equal the pair sums exactly.", 6.5)

# ---- C: one deep merge from multiz#28 -------------------------------------------------------------------------
CY = 254
text(8, CY, "C", 11, weight="bold")
text(22, CY, "One deep merge, as recorded in multiz#28", 8, weight="bold")
kl, kpl = MERGE_ROWS_A * MERGE_ROWS_B, MERGE_ROWS_A + MERGE_ROWS_B
text(262, CY, f"Blocks of about K = {MERGE_ROWS_A} rows against L = {MERGE_ROWS_B}:", 6.5)
text(262, CY + 11, f"K × L = {kl:,} row pairs per cell", 7, weight="bold", fill=VERMILION)
text(262, CY + 22, f"K + L = {kpl} rows summarised per column", 7, weight="bold", fill=GREEN)
text(262, CY + 42, f"{MERGE_S_113 / MERGE_S_114:.1f}× faster on this merge,", 8, weight="bold")
text(262, CY + 53, "identical output (single upstream runs)", 6.5)
bx0, bw, top = 50, 190, CY + 12                          # zero baseline at bx0, bw points = 1000 s
for i, (lab, s, col) in enumerate([("11.3", MERGE_S_113, VERMILION), ("11.4", MERGE_S_114, GREEN)]):
    y = top + i * 18
    rect(bx0, y, bw * s / 1000, 12, col)
    text(bx0 - 6, y + 8.5, lab, 7, "end")
    text(bx0 + bw * s / 1000 + 4, y + 8.5, f"{s} s", 7)
line(bx0, top - 3, bx0, top + 35, INK, 0.7)              # L-frame: zero baseline
line(bx0, top + 35, bx0 + bw, top + 35, INK, 0.7)
for v in (0, 250, 500, 750, 1000):
    x = bx0 + bw * v / 1000
    line(x, top + 35, x, top + 38, INK, 0.6)
    text(x, top + 46, f"{v:,}", 6, "middle")
text(bx0 + bw / 2, top + 56, "seconds", 6.5, "middle")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {FONT}>\n'
       '<defs><marker id="arrow" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="5" markerHeight="5" '
       'orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#000000"/></marker></defs>\n'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>\n' + "\n".join(el) + "\n</svg>\n")
out = HERE / "figure1.svg"
out.write_text(svg, encoding="utf-8")
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(out.with_suffix(".pdf")), str(out)], check=True)
print("wrote", out, "and", out.with_suffix(".pdf"))
