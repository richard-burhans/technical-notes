# Column counts in MULTIZ: `yama` no longer costs K × L per cell

**[Read the technical note (PDF, 7 pages)](paper/multiz_column_counts.pdf)** · Richard Burhans · 5 November 2026 · CC0

MULTIZ's `yama` aligns two alignment blocks by dynamic programming, and release 11.3 scored every cell by summing
over all K × L pairs of rows. Release 11.4 scores each cell from summaries made once per column: one score per
symbol for one block, symbol counts for the other, and counts of four gap classes. The output is unchanged. The merge as a whole still grows with the square of the depth, because scoring the merged blocks still visits every row pair.

![multiz v11.3 against v11.4 wall time as block depth grows](paper/figure2.png)

| rows per block (K = L) | v11.3 | v11.4 | speed-up | output |
|---:|---:|---:|---:|---|
| 8 | 0.34 s | 0.063 s | 5.4× | identical |
| 32 | 4.84 s | 0.129 s | 37× | identical |
| 128 | 76.7 s | 1.22 s | 63× | identical |

At K = L = 128, `yama` itself ran about a thousand times faster (76.7 s to 0.06 s under `gprof`). The whole merge
gained 63× because scoring the merged blocks (`mafScoreRange`), which still visits every row pair, now takes 94% of
the run. That is the next target. A grid of unequal depths shows the 11.3 time follows K × L, not K²
([`paper/figure3.png`](paper/figure3.png)), with the pair's shape adding up to about 20 percent.

The idea is not new. Scoring a column from symbol counts is a profile (Gribskov et al. 1987), Gotoh (1994) counted gap
states per column between groups of sequences, and Kececioglu and Zhang (1998) aligned two alignments under this gap
model in essentially O(mn) time. The change was found by profiling and checked against the
literature afterwards ([`measurements/prior_art_search.md`](measurements/prior_art_search.md)).

## Reproduce

```bash
bash probe/build_multiz.sh /tmp/multiz-cc                        # v11.3 and v11.4 from their tags, both -O2
python3 probe/run_sweep.py /tmp/multiz-cc measurements/sweep.csv  # about 5 minutes
python3 probe/run_sweep.py /tmp/multiz-cc measurements/grid.csv \
    --sizes 4x4,4x16,4x64,16x4,16x16,16x64,64x4,64x16,64x64
bash probe/profile_k128.sh /tmp/multiz-cc > measurements/gprof_k128.txt   # needs the k128l128 pair from the sweep
python3 probe/swap_order.py /tmp/multiz-cc measurements/swap_order_rep1.csv --pairs 4x16,4x64,16x64   # needs the grid
```
