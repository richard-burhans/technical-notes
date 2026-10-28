# BusyBox `sort` in biocontainers: Galaxy jobs that succeed with missing data

**[Read the technical note (PDF, 5 pages)](paper/busybox_sort.pdf)** · Richard Burhans · 28 October 2026 · CC0

Most single-package biocontainers supply `sort` from BusyBox. It holds its whole input in memory and silently
ignores `-S` and `-T`. When a job's memory limit kills it in the middle of a pipe, the next command gets an empty
or truncated stream, and the pipeline still exits 0. Galaxy adds `set -e` to tool scripts, never `pipefail`, so
the job ends green.

## What happened in Galaxy

| server | how `sort` died | job | lines in the output |
|---|---|---|---|
| usegalaxy.org, vgp (Slurm, 512 MiB) | out-of-memory kill while reading | **green**, exit 0 | **0** of 16,434,823 |
| usegalaxy.org, vgp (Slurm) | SIGKILL while writing | **green**, exit 0 | 235,008 and 262,656 of 2,000,000 |
| laila (Singularity) | SIGKILL while writing | **green**, exit 0 | 242,248 of 2,000,000 |

Slurm wrote `slurmstepd: error: Detected 1 oom-kill event(s) ...` to each job's stderr. Galaxy's Slurm runner
matches only the older "Exceeded job memory limit" wording, so it did not act.

## Memory is not a fixed multiple of the input

![Peak memory per input line against line length](paper/figure1.png)

Lines of 120 to 256 bytes cost about 275 bytes each, so a sort can need 2.5× its input. A budget that covers every
length measured: **6 MB + 2.5 × input + 40 bytes × lines**.

## What to do

1. **Sort to a file, as its own command:** `sort -k1,1 -k2,2n -o sorted.bed in.bed`. `set -e` then sees a kill.
2. **If the sort must stay in a pipe, set `pipefail` inside the script that runs it.** Avoid an early-closing
   consumer such as `head`, which turns `pipefail` into a false failure (exit 141).
3. **For large sorts, require `coreutils`**, so GNU `sort`, which spills to disk, comes first on PATH.
4. **Lint for it.** [`probe/check_midpipe_sort.py`](probe/check_midpipe_sort.py) flags `sort` before the end of a
   pipeline. In tools-iuc it finds 6 wrappers. The only one sorting data-sized input already sets `pipefail`.
5. **Have Galaxy's Slurm runner recognise `Detected N oom-kill event(s)`.**

## Reproduce

| file | what it does |
|---|---|
| [`probe/probe_container.py`](probe/probe_container.py) | the Docker measurements, and `--sweep` for the figure |
| [`probe/busybox_sort_probe.gxtool.yml`](probe/busybox_sort_probe.gxtool.yml) | the user-defined Galaxy tool run on each server |
| [`probe/probe_galaxy.py`](probe/probe_galaxy.py) | registers it, runs each mode, records state, exit code, streams, metrics and output |
| [`measurements/`](measurements/) | the raw job records, the line-length sweep, and the dated prior-art search |
