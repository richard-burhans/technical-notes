#!/usr/bin/env python3
"""A prototype lint rule: flag Galaxy tools that run `sort` anywhere but last in a pipeline.

    check_midpipe_sort.py <tools-dir> [--list]
    check_midpipe_sort.py --self-test

A sort that is not the last command of its pipeline can be killed without changing the pipeline's exit
status, and in a container whose `sort` is BusyBox that kill is how a job that ran out of memory ends green
with an empty or truncated output. Each tool is parsed with Galaxy's own parser, so macros are expanded.

A tool is reported in one of two groups:
  * BusyBox likely: no `coreutils` requirement, so a single-package biocontainer supplies BusyBox `sort`;
  * coreutils: a `coreutils` requirement, so the mulled container should put GNU `sort` first on PATH.

This reads the command TEXT, before Cheetah renders it: a sort inside an `#if` counts even if the branch is
rarely taken, and a pipeline built across Cheetah lines is split on newlines. It is an estimate.
Run it with planemo's interpreter, which has galaxy.tool_util: `~/.local/share/uv/tools/planemo/bin/python`.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

# Separators between pipelines. A single `|` (not `||`) separates commands within one.
PIPELINE_SPLIT = re.compile(r"&&|\|\||;|\n")
PIPE = re.compile(r"(?<!\|)\|(?!\|)")
# Leading words that do not change which program runs: env assignments, `env`, `LC_ALL=C`, `command`.
LEADING = re.compile(r"^(?:\s*(?:env|command|\w+=\S*)\s+)*")


def midpipe_sorts(command: str) -> list[str]:
    """The pipelines in a command text in which a `sort` runs and is not the last command."""
    hits = []
    # A pipe at the end or start of a line continues the pipeline on the next line, as does a backslash.
    text = re.sub(r"\\\n", " ", command)
    text = re.sub(r"(?<!\|)\|[ \t]*\n\s*", "| ", text)
    text = re.sub(r"\n\s*\|(?!\|)", " |", text)
    for pipeline in PIPELINE_SPLIT.split(text):
        stages = [s.strip() for s in PIPE.split(pipeline)]
        if len(stages) < 2:
            continue
        for stage in stages[:-1]:
            body = LEADING.sub("", stage.lstrip("( "))
            if re.match(r"sort(\s|$)", body):
                hits.append(" | ".join(stages)[:160])
                break
    return hits


def self_test() -> int:
    cases = {
        "cut -f1 x | sort | uniq -c > out": 1,
        "LC_ALL=C sort -k1,1 in | gzip > out": 1,
        "sort -k1,1 -o out in": 0,
        "cat in | sort -n > out": 0,
        "a || sort x": 0,
        "samtools sort -o out in | cat": 0,
        "x | env LC_ALL=C sort -u | y && z": 1,
        "cut -f1 x\n    | sort -k1,1\n    | uniq > out": 1,
        "cut -f1 x |\n  sort -u |\n  uniq > out": 1,
        "cut -f1 x \\\n  | sort \\\n  | uniq": 1,
        "a\nsort -o out in": 0,
    }
    bad = [(c, n, len(midpipe_sorts(c))) for c, n in cases.items() if len(midpipe_sorts(c)) != n]
    for c, want, got in bad:
        print(f"FAIL {c!r}: want {want}, got {got}")
    print("self-test", "FAILED" if bad else "passed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", type=pathlib.Path)
    ap.add_argument("--list", action="store_true", help="print every flagged tool and pipeline")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test or args.root is None:
        return self_test()

    from galaxy.tool_util.parser import (
        get_tool_source,  # pyright: ignore[reportMissingImports]
    )

    tools = flagged_busybox = flagged_coreutils = errors = 0
    for path in sorted(args.root.rglob("*.xml")):
        try:
            text = path.read_text(errors="replace")
            if "<tool" not in text or "<command" not in text:
                continue
            src = get_tool_source(str(path))
            command = src.parse_command() or ""
            reqs = src.parse_requirements()[0]
        except Exception:  # noqa: BLE001 -- any malformed XML or macro is counted and skipped
            errors += 1
            continue
        tools += 1
        hits = midpipe_sorts(command)
        if not hits:
            continue
        coreutils = any(getattr(r, "name", "") == "coreutils" for r in reqs)
        if coreutils:
            flagged_coreutils += 1
        else:
            flagged_busybox += 1
        if args.list:
            group = "coreutils" if coreutils else "BusyBox likely"
            print(f"{path.relative_to(args.root)}  [{group}]")
            for h in hits:
                print(f"    {h}")
    print(f"tools parsed: {tools} (skipped {errors} that did not parse)")
    print(f"sort before the end of a pipeline: {flagged_busybox + flagged_coreutils} tools")
    print(f"  without a coreutils requirement (BusyBox likely): {flagged_busybox}")
    print(f"  with a coreutils requirement: {flagged_coreutils}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
