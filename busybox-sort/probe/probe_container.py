#!/usr/bin/env python3
"""BusyBox sort in biocontainers: in memory, -S/-T ignored, and an OOM kill that a pipeline hides.

The container measurements in the BusyBox sort note, run in the container a Galaxy tool would run in:

    probe_container.py                          # all six measurements, ~5 minutes
    probe_container.py --image <img> --cap 64m --lines 2000000 --trials 3
    probe_container.py --sweep                  # peak memory against line length, for the figure

1. Which `sort` and `sh` the image ships, and whether the long GNU options are accepted.
2. Whether `-S`/`-T` (GNU's spill-to-disk knobs) do anything: the peak and the files written to the
   `-T` directory, with and without them.
3. Peak memory (`memory.peak` of the container's cgroup) against line length. The input is generated
   inside the pipe, so no page cache is counted; its byte count comes from a separate identical run.
4. A sort from a file under a `docker --memory` cap that sort's own growth exceeds, piped into an awk
   line count, with and without `set -o pipefail`.
5. The mid-write kill: a cap sort fits under, and a second process that allocates 60 MB once sort has
   started writing. Plus the control without the second process.
6. `pipefail`'s false failure: `sort | head -1`, which exits 141 when head closes the pipe early.

Docker must be available. Working files go under --workdir (default: bench/data/tmp/bbsort).
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

DEFAULT_IMAGE = "quay.io/biocontainers/ucsc-maftobigmaf:482--h0b57e2e_0"
DEFAULT_WORKDIR = Path("/home/rcb112/project/claude/bench/data/tmp/bbsort")
SWEEP_CSV = (
    Path(__file__).resolve().parent.parent / "measurements" / "line_length_sweep.csv"
)
SWEEP_BYTES = 50_000_000
SWEEP_LENGTHS = (8, 12, 16, 24, 32, 48, 64, 80, 96, 112, 120, 128, 136, 144, 160, 192, 224, 240, 256, 272, 320, 384, 512, 768, 1024)
# Line formats for the line-length measurement. The second is the one the capped runs use: chromosome,
# a random start (the sort key), a row number and a payload, about 52 bytes a line.
FORMATS = {
    "short": ("%d", 2_000_000),
    "bed-like": ("chr%d\\t%d\\t%d\\tblock_%d_padding_text_xx", 2_000_000),
    "1 KB": ("%01000d", 50_000),
}
CAPPED_FORMAT = FORMATS["bed-like"][0]
# Once sort has started writing (the consumer touches /tmp/started on its first line and reads slowly),
# a second process in the same cgroup allocates 60 MB, and the OOM killer picks the largest: sort.
MID_WRITE = (
    "( while [ ! -e /tmp/started ]; do sleep 0.05; done; sleep 0.5; "
    'awk \'BEGIN{s=sprintf("%60000000s",""); system("sleep 20")}\' ) & '
    'sort -k2,2n /w/in.tsv | awk \'NR==1{system("touch /tmp/started")} NR%200000==0{system("sleep 0.3")} '
    "END{print NR}' > /w/count; "
    'echo "rc=$? pipestatus=${PIPESTATUS[*]} lines=$(cat /w/count)"'
)


def generator(fmt: str, n: int) -> str:
    """An awk command printing n lines of fmt, with a random sort key in the second field."""
    return (
        f'awk "BEGIN{{srand(7); for(i=0;i<{n};i++) printf \\"{fmt}\\n\\", i%10, int(rand()*1e9), i, i}}"'
        if fmt.count("%") > 1
        else f'awk "BEGIN{{srand(7); for(i=0;i<{n};i++) printf \\"{fmt}\\n\\", int(rand()*1e9)}}"'
    )


def docker(
    image: str, script: str, *, cap: str | None = None, workdir: Path | None = None
) -> tuple[int, str]:
    """Run `sh -c script` in the image; return docker's exit code and combined output."""
    cmd = ["docker", "run", "--rm"]
    if cap:
        cmd += ["--memory", cap, "--memory-swap", cap]
    if workdir:
        cmd += ["-v", f"{workdir}:/w"]
    cmd += [image, "sh", "-c", script]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def sweep(image: str) -> None:
    """Peak memory of sorting ~50 MB of fixed-width numeric lines, for each line length (newline included)."""
    _, base = docker(image, "cat /sys/fs/cgroup/memory.peak")
    rows = ["line_bytes,lines,input_bytes,peak_bytes,empty_container_peak_bytes"]
    for length in SWEEP_LENGTHS:
        n = SWEEP_BYTES // length
        gen = f'awk "BEGIN{{srand(7); for(i=0;i<{n};i++) printf \\"%0{length - 1}d\\n\\", int(rand()*1e7)}}"'
        _, size = docker(image, f"{gen} | wc -c")
        _, out = docker(
            image, f"{gen} | sort -n | wc -l; cat /sys/fs/cgroup/memory.peak"
        )
        lines, peak = out.split()[-2:]
        rows.append(f"{length},{lines},{int(size)},{peak},{int(base)}")
        print(rows[-1])
    SWEEP_CSV.parent.mkdir(parents=True, exist_ok=True)
    SWEEP_CSV.write_text("\n".join(rows) + "\n")
    print(f"wrote {SWEEP_CSV}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--workdir", type=Path, default=DEFAULT_WORKDIR)
    parser.add_argument(
        "--cap",
        default="64m",
        help="docker --memory for the capped runs (measurement 4)",
    )
    parser.add_argument(
        "--mid-write-cap", default="200m", help="docker --memory for measurement 5"
    )
    parser.add_argument(
        "--lines",
        type=int,
        default=2_000_000,
        help="input lines for measurements 4 and 5",
    )
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="only the line-length sweep, written to a CSV",
    )
    args = parser.parse_args()
    args.workdir.mkdir(parents=True, exist_ok=True)
    if args.sweep:
        sweep(args.image)
        return

    print(f"== 1. image {args.image}")
    _, out = docker(
        args.image,
        "ls -l $(command -v sort) $(command -v sh); sort --help 2>&1 | head -1; "
        "for o in --buffer-size=1M --temporary-directory=/tmp --parallel=2; do "
        'echo x | sort $o >/dev/null 2>&1; echo "sort $o: rc=$?"; done',
    )
    print(out)

    print("== 2. -S/-T, 1,000,000 lines")
    for opts in ("", "-S 1M -T /tmp/spill"):
        _, out = docker(
            args.image,
            f"mkdir -p /tmp/spill; {generator(CAPPED_FORMAT, 1_000_000)} | sort {opts} -k2,2n | wc -l; "
            "cat /sys/fs/cgroup/memory.peak; ls /tmp/spill | wc -l",
        )
        lines, peak, spilled = out.split()[-3:]
        print(
            f"sort {opts or '(no -S/-T)'}: lines={lines} peak={int(peak) / 1e6:.1f} MB files in -T dir={spilled}"
        )

    print("== 3. peak memory against line length (input generated in the pipe)")
    _, out = docker(args.image, "cat /sys/fs/cgroup/memory.peak")
    print(f"empty container: peak={int(out) / 1e6:.1f} MB")
    for name, (fmt, n) in FORMATS.items():
        _, size = docker(args.image, f"{generator(fmt, n)} | wc -c")
        _, out = docker(
            args.image,
            f"{generator(fmt, n)} | sort -k2,2n | wc -l; cat /sys/fs/cgroup/memory.peak",
        )
        lines, peak = (int(v) for v in out.split()[-2:])
        size = int(size)
        print(
            f"{name}: lines={lines} input={size / 1e6:.1f} MB ({size / n:.0f} B/line) peak={peak / 1e6:.1f} MB "
            f"peak/input={peak / size:.2f} (peak-input)/line={(peak - size) / n:.0f} B"
        )

    infile = args.workdir / "in.tsv"
    if not infile.exists() or sum(1 for _ in infile.open()) != args.lines:
        docker(
            args.image,
            f"{generator(CAPPED_FORMAT, args.lines)} > /w/in.tsv",
            workdir=args.workdir,
        )
    print(
        f"== 4. capped at {args.cap}: cat in.tsv ({infile.stat().st_size / 1e6:.1f} MB) | sort | awk count"
    )
    for mode in ("", "set -o pipefail; "):
        for trial in range(1, args.trials + 1):
            script = (
                f"{mode}cat /w/in.tsv | sort -k2,2n | awk 'END{{print NR}}' > /w/count; "
                'echo "rc=$? pipestatus=${PIPESTATUS[*]} lines=$(cat /w/count)"'
            )
            rc, out = docker(args.image, script, cap=args.cap, workdir=args.workdir)
            print(
                f"[{mode.strip() or 'no pipefail'}] trial {trial}: {out} (docker rc={rc})"
            )

    print(
        f"== 5. mid-write kill at {args.mid_write_cap}: sort | slow awk count, 60 MB allocated once output starts"
    )
    script = "sort -k2,2n /w/in.tsv | awk 'END{print NR}'; echo \"control: rc=$? pipestatus=${PIPESTATUS[*]}\""
    print(docker(args.image, script, cap=args.mid_write_cap, workdir=args.workdir)[1])
    for trial in range(1, args.trials + 1):
        rc, out = docker(
            args.image, MID_WRITE, cap=args.mid_write_cap, workdir=args.workdir
        )
        print(f"trial {trial}: {out} (docker rc={rc})")

    print("== 6. pipefail and an early-closing consumer")
    print(
        docker(
            args.image,
            'set -o pipefail; seq 100000 | sort -n | head -1 >/dev/null; echo "rc=$? ps=${PIPESTATUS[*]}"',
        )[1]
    )


if __name__ == "__main__":
    main()
