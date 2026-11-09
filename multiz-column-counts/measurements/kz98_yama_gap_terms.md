# yama's gap charges against Kececioglu and Zhang 1998, eqs. (42)-(44)

**Verdict on 23-h844bde: HOLDS WITH CHANGES.** All 16 class-pair charges and all nine transition sums equal the pessimistic case of (42)-(44). But yama's free end gaps reach into the interior equations as well as (45)-(53). It drops every gap open of (42) at i = m, of (44) at j = 1, and of (43) at j = n.

Code read: upstream multiz/multiz tag v11.4 (6bfe6a4, the same commit in the richard-burhans fork) and tag v11.9 (077e847). The v11.9 `mz_yama.c`, `mz_preyama.c` and `mz_scores.c` are byte-identical to the fork checkout `bench/data/multiz/multiz-119` at c0e4922. Line numbers below are at v11.4 unless marked v11.9.

Paper: `bench/data/papers/kececioglu_1998_aligning.pdf`. Equations come from page renders at 200 and 400 dpi, not from the OCR layer.

## Symbols and directions

| KZ98 | yama |
|---|---|
| A is k x m, columns i | A is K x M, `row` |
| B is l x n, columns j | B is L x N, `col` |
| H(i,j): insert column j of B against nulls | I node |
| V(i,j): delete column i of A against nulls | D node |
| D(i,j): substitute column i against column j | C node |
| cost, minimised | score, maximised. score = -cost |
| delta(a,b) | `-ss[a][b]` |
| gamma (gap start-up) | `gap_open`, 400 for HOXD70 |
| lambda (gap extension) | `gap_extend`, 30 for HOXD70 |
| null character epsilon | `'-'` |
| beta = 1 for a non-null character | dash flag = 1 for `'-'`. So beta = 1 - flag |

KZ98 p. 191 sets delta(a,eps) = delta(eps,a) = lambda and delta(eps,eps) = 0. yama sets `ss['-'][i] = ss[i]['-'] = -gap_ex` and `ss['-']['-'] = 0` (mz_scores.c:53-55).

## Gamma, p. 194

Rows a1a2, columns b1b2. 1 means non-null. a1 and b1 are the previous column, a2 and b2 the current one.

```
        00     01     10   11
  00     0   {0,1}     0    0
  01  {0,1}    0       1    0
  10     0     1       0    1
  11     0     0       1    0
```

The two {0,1} entries are 0 for optimistic counts and 1 for pessimistic counts (p. 194). B gets an artificial column 0 of non-null characters (beta_{i0} = 1, p. 194). f_x(j), f_xy(j) and f_perp1(j) are defined on p. 195. Section 4.1 (p. 201) says the alignment-vs-alignment counts f^A_00 ... f^A_11, f^B_00 ... f^B_11, f^A_perp1 and f^B_perp1 are "defined as for the sequence vs. alignment case".

## Equations (42)-(53), transcribed from printed pp. 205-206 (PDF pp. 17-18)

The page labels each case "opt" or "pess", each followed by punctuation. Here they are written [opt] and [pess]. Every symbol was legible at 400 dpi. The subscript of f in (45), (46), (48) and (49) is a perpendicular sign followed by 1, written perp1.

For i > 0 and j > 0 (p. 205):

```
(42) H(i,j) = lambda k f1^B(j)
       + min { H(i,j-1) + gamma { 0                                   [opt]
                                  k f01^B(j)                          [pess] }
               V(i,j-1) + gamma { f1^A(i) f1^B(j)                     [opt]
                                  k f1^B(j)                           [pess] }
               D(i,j-1) + gamma { f1^A(i) f1^B(j)                     [opt]
                                  f1^A(i) f1^B(j) + f0^A(i) f01^B(j)  [pess] } }
```

p. 205 ends with "V(i,j) = lambda l f1^A(i)" and p. 206 continues it:

```
(43) V(i,j) = lambda l f1^A(i)
       + min { H(i-1,j) + gamma { f1^A(i) f1^B(j)                     [opt]
                                  l f1^A(i)                           [pess] }
               V(i-1,j) + gamma { 0                                   [opt]
                                  l f01^A(i)                          [pess] }
               D(i-1,j) + gamma { f1^A(i) f1^B(j)                     [opt]
                                  f1^A(i) f1^B(j) + f01^A(i) f0^B(j)  [pess] } }

(44) D(i,j) = sum_{a,b in Sigma U {eps}} fa^A(i) fb^B(j) delta(a,b)
       + min { H(i-1,j-1) + gamma { f1^A(i) f10^B(j)                  [opt]
                                    f1^A(i) f0^B(j) + f0^A(i) f01^B(j)  [pess] }
               V(i-1,j-1) + gamma { f10^A(i) f1^B(j)                  [opt]
                                    f0^A(i) f1^B(j) + f01^A(i) f0^B(j)  [pess] }
               D(i-1,j-1) + gamma { f1^A(i) f10^B(j) + f10^A(i) f1^B(j)   [opt]
                                    f1^A(i) f10^B(j) + f10^A(i) f1^B(j)
                                    + f00^A(i) f01^B(j) + f01^A(i) f00^B(j)  [pess] } }
```

Boundaries (p. 206):

```
For i = 0 and j > 0:
(45) H(0,j) = H(0,j-1) + lambda k f1^B(j) + gamma k fperp1^B(j)
(46) V(0,j) = H(0,j) + gamma l fperp1^A(1)
(47) D(0,j) = V(0,j)
For i > 0 and j = 0:
(48) V(i,0) = V(i-1,0) + lambda l f1^A(i) + gamma l fperp1^A(i)
(49) H(i,0) = V(i,0) + gamma k fperp1^B(1)
(50) D(i,0) = H(i,0)
For i = 0 and j = 0:
(51) V(0,0) = 0
(52) H(0,0) = 0
(53) D(0,0) = 0
```

## The 16 class-pair charges

yama charges `GAP(s,t,u,v) = gop[(s<<3)+(t<<2)+(u<<1)+v]` per row pair (mz_scores.h:16). s and u are A's dash flags in the previous and current column, t and v are B's. `gop` is `gap_open` at six entries and 0 elsewhere (mz_scores.c:79-80). With beta = 1 - flag, those six are exactly the six 1-entries of pessimistic Gamma:

| yama (s,t,u,v) | KZ Gamma(a1a2, b1b2) |
|---|---|
| (0,0,0,1) | (11,10) = 1 |
| (0,0,1,0) | (10,11) = 1 |
| (0,1,1,0) | (10,01) = 1 |
| (1,0,0,1) | (01,10) = 1 |
| (1,1,0,1) | (01,00) = 1 [pess] |
| (1,1,1,0) | (00,01) = 1 [pess] |

So `GAP(s,t,u,v) = gamma * Gamma_pess((1-s)(1-u), (1-t)(1-v))` for all 16 inputs. The mz_scores.c comment (lines 62-77) says the last two "may result in a gap being counted twice". That is the pessimistic case. The executable check below reads `gop` from both compiled releases and finds 16 of 16 equal.

## Class bookkeeping

yama gives each row a class `CL(prev dash, cur dash)` (mz_yama.c:52). In KZ terms:

| yama count | KZ count |
|---|---|
| `cnt[row][0]`, `gb[col][0]` | f11^A(i), f11^B(j) |
| `cnt[row][1]`, `gb[col][1]` | f10^A(i), f10^B(j) |
| `cnt[row][2]`, `gb[col][2]` | f01^A(i), f01^B(j) |
| `cnt[row][3]`, `gb[col][3]` | f00^A(i), f00^B(j) |
| `ua[row][0]`, `vb[col][0]` | f1^A(i), f1^B(j) |
| `ua[row][1]`, `vb[col][1]` | f0^A(i), f0^B(j) |

The previous column of row 1 counts as non-dash: `s = (row > 1 && A[row-1][i] == '-')` (mz_yama.c:166) and `t = (col > 1 && B[col-1][j] == '-')` (mz_yama.c:141). That is KZ's artificial non-null column 0. yama keeps no f_perp1 count, because it charges no opens on the boundary.

## Term by term

Each yama term is a sum over the 4 x 4 (or 2 x 2) class pairs of count x count x `GAP`, with the A side folded into the per-row table `rt[row]` (mz_yama.c:173-202). It is never reduced to KZ's sparse form. The "KZ pess" column is the bracketed factor that gamma multiplies.

| KZ eq. | transition | KZ pess | yama term (v11.4 line) | equal? | where yama drops it |
|---|---|---|---|---|---|
| (42) | H from H | k f01^B(j) | `z -= gb[col][k]*Iz[k]`, `Iz = K*GAP(1,t,1,v)` (237, 159) | yes | i = m (232) |
| (42) | H from V | k f1^B(j) | `y -= vb*rt.Iy`, `Iy[t] = sum ua[s]*GAP(s,1,1,t)` (239, 193) | yes | i = m (232) |
| (42) | H from D | f1^A f1^B + f0^A f01^B | `x -= gb[col][k]*rt.Ix[k]`, `Ix = sum ua[s]*GAP(s,t,1,v)` (235, 195) | yes | i = m (232) |
| (43) | V from H | l f1^A(i) | `z -= vb*rt.Dz`, `Dz[t] = sum ua[u]*GAP(1,t,u,1)` (313, 199) | yes | j = n (306) |
| (43) | V from V | l f01^A(i) | `y -= rt.Dy`, `Dy = sum cnt*L*GAP(s,1,u,1)` (311, 183) | yes | j = n (306) |
| (43) | V from D | f1^A f1^B + f01^A f0^B | `x -= vb*rt.Dx`, `Dx[t] = sum cnt*GAP(s,t,u,1)` (309, 185) | yes | j = n (306) |
| (44) | D from H | f1^A f0^B + f0^A f01^B | `z -= gb*rt.Cz`, `Cz = sum ua[u]*GAP(1,t,u,v)` (279, 201) | yes | j = 1 (274) |
| (44) | D from V | f0^A f1^B + f01^A f0^B | `y -= vb*rt.Cy`, `Cy[v] = sum cnt*GAP(s,1,u,v)` (282, 186) | yes | j = 1 (274) |
| (44) | D from D | f1^A f10^B + f10^A f1^B + f00^A f01^B + f01^A f00^B | `x -= gb*rt.Cx`, `Cx = sum cnt*GAP(s,t,u,v)` (277, 188) | yes | j = 1 (274) |
| (42) | extension | lambda k f1^B(j) | `I -= n*K*gap_extend`, `n = vb[col][0]` (261-262) | yes | never |
| (43) | extension | lambda l f1^A(i) | `D -= n*L*gap_extend`, `n = ua[row][0]` (328-329) | yes | never |
| (44) | substitution | sum f_a^A f_b^B delta(a,b) over Sigma U {eps} | `C += n*wA[row][k]` over symbols (294-296) | yes, with delta = -ss | never |

In v11.9 the same terms sit at mz_yama.c:262-267 (I), 290-300 (C) and 310-324 (D). The I-from-I sum there is precomputed per column as `Izc` (v11.9:231-233).

The guards `row < M`, `col > 1` and `col < N` are the drops in the last column. The other guards (`col > LB[row-1]+1`, `col > LB[row]+1`, `row > 1 && col > LB[row-2]+1`, `row > 1`) skip a term only when its predecessor lies outside the band or on row 0, where its value is `MININT`. I read this from the code. The check below used a full band only.

Asymmetry: D-state opens (yama's C node) are free at j = 1 but charged at i = 1. The C-from-I term at row 1 (`z`, line 278-279) has no row guard. So C(1,j) still pays opens from H(0,j-1) for j > 1.

## Boundaries and ends

| KZ | yama | same? |
|---|---|---|
| (51)-(53) all zero | `dp[0].C = dp[0].D = dp[0].I = 0` (108) | yes |
| (45) H(0,j) charges lambda k f1^B + gamma k fperp1^B | `dp[col].I = dp[col-1].I - n*K*gap_extend` (115) | extension only, no gamma term |
| (46), (47) V(0,j) = D(0,j) = H(0,j) + gamma l fperp1^A(1) | `dp[col].C = dp[col].D = MININT` (111) | no. Unreachable in yama |
| (48) V(i,0) charges lambda l f1^A + gamma l fperp1^A | D node at col 0. The open guard `0 < col` is false (306). Extension at 328-329 | extension only, no gamma term |
| (49), (50) H(i,0) = D(i,0) = V(i,0) + gamma k fperp1^B(1) | I and C at col 0 are `MININT`, since `col > LB[row]` (223) and `col > LB[row-1]` (270) fail | no. Unreachable in yama |
| end: best of the three states at (m,n) | best of C, D, I at (M,N), ties to C then D (349-354) | yes. KZ states this end rule on p. 192 for sequence vs. sequence. Appendix A does not restate it |

So the boundary part of the claim is right: (45)-(50) do not apply. yama keeps their extension terms and drops their gamma terms. (51)-(53) agree. But "free end gaps" is wider than the boundary. yama's comment says "End-gaps (overhangs) are not charged a gap-open penalty" (mz_yama.c:16), and it implements that with three guards inside the interior:

1. `if (row < M)` (232): every H open at i = m, the trailing insertions after A ends.
2. `if (col > 1)` (274): every D-state open at j = 1, for all i.
3. `if (0 < col && col < N)` (306): every V open at j = n, the trailing deletions after B ends.

Guard 2 is not only an end-gap rule. At C(i,1) for i > 1 it waives opens of interior gaps in A's rows (round 24 L1 F2 has an example where it changes yama's output). Guards 1 and 3 free only trailing gaps.

So yama equals pessimistic (42)-(44) on 1 <= i < m for H, 2 <= j for D, and 1 <= j < n for V, with all opens dropped on the three lines above and the extension-only boundary.

The second call, `yama(A2, 1, M3, AL_new, ...)` (mz_preyama.c:340 at v11.9), passes one dash-free row (`rmColDash`, mz_preyama.c:282). This is the k = 1 case of the same equations. With f1^A = 1 and f0^A = f01^A = 0, (42) reduces to KZ's (16).

## Executable check

Files: `probe/kz98_yama/kz_vs_yama.py` and `probe/kz98_yama/main.c`. `probe/kz98_yama/build_and_run.sh WORKDIR [SEED]` clones multiz v11.4 and v11.9, builds both harnesses and runs the script; outputs are `measurements/kz98_yama_seed7.txt` and `kz98_yama_seed11.txt` (regenerated on 2026-11-09 by the committed script from fresh clones pinned to 6bfe6a4 and 077e847; step [1] runs on both binaries; step [3] is a random sample of 1000 blocks per seed, not an exhaustive enumeration of blocks, though each block's paths are enumerated exhaustively). The harness links the real `mz_yama.c`, `mz_scores.c` and `util.c` of v11.4 and of v11.9 with `init_scores70()` and a full band, and prints yama's output alignment. The script does three things:

1. It compares `gop[16]` from the binary with gamma x pessimistic Gamma.
2. On random paths it compares each interior step's opens from the transcribed closed forms (42)-(44) with the pair-by-pair Gamma sum.
3. On random blocks (K, L up to 4 rows, M, N up to 5 columns, bytes `ACGTacgtN-`, no all-dash column) it enumerates every path. It asks whether yama's output reaches the brute-force optimum under several models of which opens are free. Model Y is my reading. It uses pessimistic Gamma everywhere and frees opens on I at rows 0 and M, C at column 1, and D at columns 0 and N. Y0 is the claim as worded, with only the boundary free. P frees nothing. The other models change one drop of Y.

Output, seed 7 (`measurements/kz98_yama_seed7.txt`):

```
[1] yama_v11.4: gop[16] vs gap_open*Gamma_pess(1-s 1-u, 1-t 1-v): 16/16 equal
[1] yama_v11.9: gop[16] vs gap_open*Gamma_pess(1-s 1-u, 1-t 1-v): 16/16 equal
[2] interior steps checked: 8740, closed form != Gamma sum: 0
[3] yama_v11.4: 1000 random cases, yama output optimal under Y: 1000/1000, Y0: 214/1000, Y-noIrowM: 621/1000, Y-noCcol1: 805/1000, Y-noDcolN: 521/1000, Y+Crow1: 830/1000, P: 235/1000
[3] yama_v11.9: 1000 random cases, yama output optimal under Y: 1000/1000, Y0: 214/1000, Y-noIrowM: 621/1000, Y-noCcol1: 805/1000, Y-noDcolN: 521/1000, Y+Crow1: 830/1000, P: 235/1000
```

Output, seed 11 (`measurements/kz98_yama_seed11.txt`):

```
[1] yama_v11.4: gop[16] vs gap_open*Gamma_pess(1-s 1-u, 1-t 1-v): 16/16 equal
[1] yama_v11.9: gop[16] vs gap_open*Gamma_pess(1-s 1-u, 1-t 1-v): 16/16 equal
[2] interior steps checked: 8870, closed form != Gamma sum: 0
[3] yama_v11.4: 1000 random cases, yama output optimal under Y: 1000/1000, Y0: 220/1000, Y-noIrowM: 581/1000, Y-noCcol1: 812/1000, Y-noDcolN: 573/1000, Y+Crow1: 853/1000, P: 250/1000
[3] yama_v11.9: 1000 random cases, yama output optimal under Y: 1000/1000, Y0: 220/1000, Y-noIrowM: 581/1000, Y-noCcol1: 812/1000, Y-noDcolN: 573/1000, Y+Crow1: 853/1000, P: 250/1000
```

Reading: the transcribed closed forms equal the Gamma sums. yama's output is optimal under Y in every case. Removing any one of the three interior drops, or adding a row-1 drop for symmetry, breaks that. The claim as worded (Y0) matches only about a fifth of cases.

## 23-hc07473: 11.4's per-cell cost in KZ98's symbols

Derived from v11.4 mz_yama.c:

- **Substitution.** For each column i of A, `wA[i][b] = sum_r ss(a_ri, b)` (170-171). That is `sum_{a in Sigma U {eps}} f_a^A(i) sigma(a,b)`, built from the rows directly. For each column j of B, `hist[j][b] = f_b^B(j)` (145). The cell adds `sum_b f_b^B(j) wA[i][b]` (294-296). This is KZ's double sum in (44), factored with the A side summed first. It has one term per symbol b, not s^2 terms.
- **What s counts.** The loop runs over `nsym` symbols. `nsym` is the number of distinct byte values anywhere in block B as passed to yama (124-131). That block has its all-dash columns removed (mz_preyama.c:183 at v11.9). It does not count the whole alphabet, and it does not count only the current column. It is case-sensitive in 11.4. It includes the dash whenever any row of B has one. In KZ's terms, nsym = |Sigma_B| + [eps occurs in B], where Sigma_B is the part of Sigma present in B. KZ's Theorem 4 uses s = the alphabet size (p. 201) and sums over Sigma U {eps}. In 11.4 a symbol absent from column j still costs one loop step and a zero test. 11.5 and later merge symbols whose `ss` columns are identical (v11.9 mz_yama.c:141-156). Under HOXD70 and HOXD85 that leaves at most six classes: A, C, G, T in either case, the dash, and one class for every other byte. I found this by reading `init_scores`, not by running it.
- **The dash.** It is KZ's eps. It enters the substitution sum with `ss = -gap_extend` against a base and 0 against a dash. So the C node's sum charges lambda for every base-against-null pair in a substitution column, as KZ's (44) does through delta(a,eps) = lambda. A count that left out the dash would drop those lambda terms.
- **Gaps.** These are per-cell dot products against precomputed per-row tables: I has 4 + 4 + 2, C has 4 + 4 + 2, and D has 2 + 1 + 2 multiply-adds. That makes 25, plus 2 for extension. The count does not depend on k, l or s.
- **Totals.** Precomputation is O(l n) for the B classes and symbol counts, O(n nsym) to clear `hist`, and O(k m nsym) for `wA`. The class tables are O(1) per column of A. The DP is O(nsym) per cell over the band, at most (m+1)(n+1) cells. For a full band that is O(nsym km + l n + nsym mn), plus O((m+n)(k+l)) to write the output block, an output-size term every method pays rather than a per-cell cost (round 24 L1 F4). KZ's Theorem 4 is O(km + l n + min{s^2, kl} mn). 11.4 pays nsym per cell, not min{s^2, kl}, and pays nsym per row entry of A once.

## What I did not check

- Banded runs. The harness used LB = 0, RB = N. I took the claim that the band guards only skip `MININT` predecessors from reading the code.
- KZ's boundary (45)-(50) was not run. I did not test whether KZ's finite V(0,j) and D(0,j) can win its min. So I cannot say how far KZ's own optimum moves when yama makes them unreachable.
- Whether KZ's Appendix A intends the same end rule as p. 192. It does not state one.
- The optimistic case, which is not claimed.
- Blocks larger than 4 x 5, or bytes outside `ACGTacgtN-`.
- The six-class bound for 11.5 and later, and the per-cell operation counts, which come from reading the code and were not measured.
- KZ's proofs. The paper omits them.
- The tex wording. Round 24 rewrote the note's sentence to state the waivers per step type ("Release 11.4 computes that objective except where yama waives gap opens", multiz_column_counts.tex), which is model Y.
