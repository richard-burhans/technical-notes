# Prior-art search, 2026-10-28

`gh search issues --include-prs`, GitHub-wide unless an owner or repo is named.

| query | scope | relevant hits |
|---|---|---|
| `busybox sort` | owner galaxyproject | tools-iuc#3920 |
| `busybox sort` | owner BioContainers | containers#483 (others are unrelated mulled-container additions; multi-package-containers#3073 adds coreutils) |
| `busybox sort` | owner bioconda | bioconda-recipes#37865 (bismark), #31162 and #52229 (Trinity adds coreutils) |
| `pipefail` | galaxyproject/galaxy | galaxy#5884, galaxy#12093 / #12112 |
| `pipefail` | galaxyproject/tools-iuc | tools-iuc#4413 (Mothur: detect OOM) |
| `pipefail` | galaxyproject/planemo | none |
| `busybox sort memory` | all | nf-core/modules#13033 |
| `busybox sort out of memory` | all | none |
| `busybox sort -S ignored` | all | none |
| `busybox sort large file` | all | none |

## What each relevant hit establishes

* **galaxy#5884** (2018-04-13, closed 2022-08-19): proposes `set -o pipefail` in every tool script. Declined in
  discussion because `pipefail` "is not POSIX so it may not work when executing jobs on containers (which use `sh`
  instead of `bash`)" (nsoranzo, 2020-07-06).
* **galaxy#12093 / #12112** (2021): `pipefail` plus `head` made "Show beginning" fail on long files; fixed by
  ignoring SIGPIPE. The false failure this note describes, seen in practice.
* **tools-iuc#3920** (2021-09-03, natefoo): adds a coreutils requirement to vcfsort because BusyBox sort lacks `-V`.
* **BioContainers/containers#483** (2022-11-08) and **bioconda-recipes#37865**: bismark2bedGraph's
  `sort -S -T -k3,3V` failed in BusyBox 1.32.1, which rejected `-S`/`-T`, giving empty output files. BusyBox 1.36.1
  accepts and ignores them (this note), so the symptom changed between versions.
* **nf-core/modules#13033** (2026-09-25): hmmer's external sort shells out to `sort`, which in the biocontainer is
  BusyBox, "sorts entirely in memory, so it dies on large inputs". The in-memory design was known; that failure was
  loud.
* **tools-iuc#4413**: Mothur jobs that run out of memory are not detected. A neighbouring problem.

## Not found

No report found of a mid-pipe BusyBox sort kill producing a successful job with an empty or truncated output, in
Galaxy or elsewhere, and none of `-S`/`-T` being silently ignored. An absence from these searches, not proof.
