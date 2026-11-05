# Prior-art search, 2026-11-05

The change was found by profiling (`yama` took 98% of one deep merge), and no literature search was run before it
shipped in multiz 11.4. This is the first. Web search (US), the Europe PMC REST API, and CrossRef for every DOI.

| query | what it found |
|---|---|
| Kececioglu Starrett "Aligning alignments exactly" | Kececioglu and Starrett (RECOMB 2004), read in full |
| Gotoh 1993 "optimal alignment between groups of sequences" | Gotoh (1993), PMID 8324637, read in full |
| Gotoh 1994 "Further improvement … generalized profile operations" | Gotoh (1994), PMID 7804871, read in full |
| Altschul 1989 "Gap costs for multiple sequence alignment" | Altschul (1989), the gap model `mz_yama.c` cites, read in full |
| Gribskov profile analysis 1987 | Gribskov, McLachlan and Eisenberg (1987), read in full |
| Kececioglu Zhang 1998 "Aligning alignments" | Kececioglu and Zhang (CPM 1998), record and the 2004 paper's summary of it only |
| MUSCLE profile sum of pairs | Edgar (2004): profile-profile scoring, a different objective. Not cited |
| multiz / TBA / yama speed-up by column counts | nothing beyond the TBA paper (Blanchette et al. 2004) |

## What each source establishes

* **Gribskov et al. (1987).** The profile score of symbol a at position p is M(p,a) = Σ_b W(p,b) · Y(a,b), with Y the
  substitution matrix and the "simple average weight" W(b,p) = n(b,p)/NR. `yama`'s fold is the same sum without the
  division. Scoring by column counts is a profile.
* **Gotoh (1994).** "it is possible partly to suppress this computational augmentation by the use of profile vectors
  (Gribskov et al, 1987). However, there has been no way to evaluate the accurate gap-opening costs with computation
  steps less than O(M x N)." His contribution is the gap half, through gap-state variables computed once per column.
  He reports about 10-fold speed-ups at M × N ≈ 200 and over 100-fold at M × N > 2500.
* **Gotoh (1993).** Four group-to-group algorithms. The rigorous one, D, has "average performance … close to O(MNL²)" on four protein families. He says its worst case is not known, so this is not a bound.
* **Altschul (1989).** Quasi-natural costs add one gap in the case natural costs would need more history, so "the
  preceding edge completely determines the number of gaps a new edge introduces". That is why four dash classes
  suffice.
* **Kececioglu and Starrett (2004).** With exact gap counts, aligning two alignments is NP-complete. They call Gotoh's
  two papers "pioneering", and note that Gotoh's rigorous procedure cannot run in polynomial time unless P = NP.
  Release 11.4 computes `yama`'s quasi-natural objective and does not touch that problem.

No publication applying this reduction to MULTIZ or the threaded blockset aligner was found.
