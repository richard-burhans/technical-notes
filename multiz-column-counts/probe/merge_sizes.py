#!/usr/bin/env python3
"""Genome count on each side of every multiz call in a roast command list.

    python3 merge_sizes.py CMDS.txt > merge_sizes.tsv

CMDS.txt is roast's command list printed without running it (a dry run). The script replays the
cp, mv, echo, multiz, maf_project and grep commands, tracking which genomes each file holds, and
prints one row per multiz call: call number, genomes in A, genomes in B, genomes in the result,
genomes shared (the reference, normally 1).

Written by round 21's completeness adjudicator (cannabis-genome reports/rounds/round-21/), committed
2026-11-09. measurements/merge_sizes.tsv is its output on piece NC_044376.1.02's roast
(measurements/roast_dryrun_NC_044376.1.02.txt).
"""
from __future__ import annotations

import shlex
import sys

REF = "cs10_NCBI_RefSeq_softmasked"


def main(path: str) -> None:
    files: dict[str, set[str]] = {}

    def get(name: str) -> set[str]:
        if name in files:
            return set(files[name])
        if name.startswith(REF + ".") and name.endswith(".sing.maf"):
            return {REF, name[len(REF) + 1:-len(".sing.maf")]}
        return set()

    n = 0
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            t = shlex.split(line.strip())
            if not t:
                continue
            op = t[0]
            out, app = None, False
            if ">>" in t:
                i = t.index(">>")
                out, app, t = t[i + 1], True, t[:i]
            elif ">" in t:
                i = t.index(">")
                out, t = t[i + 1], t[:i]
            if op == "cp":
                files[t[2]] = get(t[1])
            elif op == "mv":
                files[t[2]] = get(t[1])
                files.pop(t[1], None)
            elif op == "echo" and out:
                files[out] = get(out) if app else set()
            elif op == "multiz":
                a, b = get(t[2]), get(t[3])
                n += 1
                print(n, len(a), len(b), len(a | b), len(a & b), sep="\t")
                if out:
                    files[out] = (get(out) if app else set()) | a | b
            elif op in ("maf_project", "grep") and out:
                src = t[1] if op == "maf_project" else t[-1]
                files[out] = (get(out) if app else set()) | get(src)


if __name__ == "__main__":
    main(sys.argv[1])
