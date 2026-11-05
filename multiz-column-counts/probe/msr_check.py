"""Compare upstream mafScoreRange (pairwise, as in mz_scores.c at v11.4) with a per-column count regrouping.

Usage: python3 -I msr_check.py MAF [MAF ...]
Prints, per file: blocks, blocks whose pairwise score equals the MAF score line, blocks where count == pairwise.
"""
import sys
from collections import Counter

HOX70 = [[91, -114, -31, -123], [-114, 100, -125, -31], [-31, -125, 100, -114], [-123, -31, -114, 91]]
ss = [[-100] * 128 for _ in range(128)]
for i, A in enumerate("ACGT"):
    for j, B in enumerate("ACGT"):
        for x in (A, A.lower()):
            for y in (B, B.lower()):
                ss[ord(x)][ord(y)] = HOX70[i][j]
for i in range(128):
    ss[ord("-")][i] = ss[i][ord("-")] = -30
ss[ord("-")][ord("-")] = 0
gop = [0] * 16
X, D = 0, 1
for s, t, u, v in [(X, X, X, D), (X, X, D, X), (X, D, D, X), (D, X, X, D), (D, D, X, D), (D, D, D, X)]:
    gop[(s << 3) + (t << 2) + (u << 1) + v] = 400


def pairwise(rows):
    n, score = len(rows), 0
    for i in range(len(rows[0])):
        for a in range(n):
            br = rows[a][i]
            for b in range(a + 1, n):
                bi = rows[b][i]
                score += ss[br][bi]
                if i > 0:
                    ar, ai = rows[a][i - 1], rows[b][i - 1]
                    score -= gop[((ar == 45) << 3) + ((ai == 45) << 2) + ((br == 45) << 1) + (bi == 45)]
    return score


def counted(rows):
    score = 0
    for i in range(len(rows[0])):
        n = Counter(r[i] for r in rows)
        syms = list(n)
        tot = sum(n[s] * n[t] * ss[s][t] for s in syms for t in syms) - sum(n[s] * ss[s][s] for s in syms)
        assert tot % 2 == 0
        score += tot // 2
        if i > 0:
            m = Counter(((r[i - 1] == 45), (r[i] == 45)) for r in rows)
            g = 0
            for (p1, c1), k1 in m.items():
                for (p2, c2), k2 in m.items():
                    g += k1 * k2 * gop[(p1 << 3) + (p2 << 2) + (c1 << 1) + c2]
            g -= sum(k * gop[(p << 3) + (p << 2) + (c << 1) + c] for (p, c), k in m.items())
            assert g % 2 == 0
            score -= g // 2
    return score


for path in sys.argv[1:]:
    blocks, cur, sc = [], None, None
    for line in open(path, "rb"):
        if line.startswith(b"a"):
            if cur:
                blocks.append((sc, cur))
            cur = []
            sc = float(line.split(b"score=")[1]) if b"score=" in line else None
        elif line.startswith(b"s ") and cur is not None:
            cur.append(line.split()[6])
    if cur:
        blocks.append((sc, cur))
    eq_file = eq_count = 0
    for sc, rows in blocks:
        p = pairwise(rows)
        eq_file += sc is not None and abs(sc - p) < 0.5
        eq_count += counted(rows) == p
    print(path, len(blocks), "pairwise==score line:", eq_file, "counted==pairwise:", eq_count)
