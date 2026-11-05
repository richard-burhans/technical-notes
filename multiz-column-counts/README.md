# Column counts in MULTIZ: aligning two alignments in K + L, not K × L

**[Read the technical note (PDF, 6 pages)](paper/multiz_column_counts.pdf)** · Richard Burhans · 5 November 2026 · CC0

MULTIZ's `yama` aligns two alignment blocks by dynamic programming, and release 11.3 scored every cell by summing
over all K × L pairs of rows. Release 11.4 scores each cell from summaries made once per column: one score per
symbol for one block, symbol counts for the other, and counts of four gap classes. The output is unchanged.

![multiz v11.3 against v11.4 wall time as block depth grows](paper/figure2.png)

| rows per block (K = L) | v11.3 | v11.4 | speed-up | output |
|---:|---:|---:|---:|---|
| 8 | 0.34 s | 0.063 s | 5.4× | identical |
| 32 | 4.84 s | 0.129 s | 37× | identical |
| 128 | 76.7 s | 1.22 s | 63× | identical |

At K = L = 128, `yama` itself ran about a thousand times faster (76.7 s to 0.06 s under `gprof`). The whole merge
gained 63× because scoring the merged blocks (`mafScoreRange`), which still visits every row pair, now takes 94% of
the run. That is the next target. A grid of unequal depths shows the 11.3 time depends on K × L alone
([`paper/figure3.png`](paper/figure3.png)).

Neither half is new. Scoring a column from symbol counts is a profile (Gribskov et al. 1987). Counting gap states per
column to avoid the K × L loop is Gotoh's (1994). The change was found by profiling and checked against the
literature afterwards ([`measurements/prior_art_search.md`](measurements/prior_art_search.md)).

## Reproduce

```bash
bash probe/build_multiz.sh /tmp/multiz-cc                        # v11.3 and v11.4 from their tags, both -O2
python3 probe/run_sweep.py /tmp/multiz-cc measurements/sweep.csv  # about 2 minutes
```
