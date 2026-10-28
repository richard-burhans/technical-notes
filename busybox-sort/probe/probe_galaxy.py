#!/usr/bin/env python3
"""Does Galaxy notice when BusyBox sort is killed in the middle of a pipe?

Registers the user-defined tool in busybox_sort_probe.gxtool.yml, runs it in each mode, and records
what Galaxy reports: job state, exit code, both streams, job messages, the memory metrics, and the
output dataset's state and content.

    probe_galaxy.py --host laila --modes kill --yes
    probe_galaxy.py --host vgp --modes oom-file,oom-pipe,kill --yes
    probe_galaxy.py --host main --deactivate --yes      # retire the tool when finished

Credentials come from GALAXY_URL / GALAXY_API_KEY (and the _2, _3 pairs), matched on the exact host.
vgp shares usegalaxy.org's database, so the tool is registered once on main and runs on both.
Results are appended as JSON lines to ../measurements/galaxy_runs.jsonl.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time
import urllib.parse
from typing import Any

import requests
import yaml

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "busybox_sort_probe.gxtool.yml"
OUT = HERE.parent / "measurements" / "galaxy_runs.jsonl"
HOSTS = {
    "main": "usegalaxy.org",
    "vgp": "vgp.usegalaxy.org",
    "laila": "host.docker.internal",
}
# vgp has no registry of its own: tools registered on main are visible there.
REGISTRY = {"vgp": "main"}
METRICS = (
    "galaxy_memory_mb",
    "galaxy_slots",
    "memory.peak",
    "runtime_seconds",
    "memory.max",
)


def credentials(host: str) -> tuple[str, str]:
    """(url, key) for a named host, matched exactly on the URL's host name."""
    want = HOSTS[host]
    for suffix in ("", "_2", "_3"):
        url = os.environ.get(f"GALAXY_URL{suffix}", "").strip()
        key = os.environ.get(f"GALAXY_API_KEY{suffix}", "").strip()
        if url and key and urllib.parse.urlparse(url).hostname == want:
            return url.rstrip("/"), key
    sys.exit(f"no GALAXY_URL* points at {want}")


class Galaxy:
    def __init__(self, host: str) -> None:
        self.url, key = credentials(host)
        self.s = requests.Session()
        self.s.headers["x-api-key"] = key

    def call(self, method: str, path: str, **kw: Any) -> Any:
        r = self.s.request(method, self.url + path, timeout=120, **kw)
        r.raise_for_status()
        return r.json() if r.content else None


def tool_uuid(g: Galaxy, rep: dict, *, create: bool) -> str | None:
    """The uuid of the active registration of this id and version, registering it if asked."""
    for row in g.call("GET", "/api/unprivileged_tools") or []:
        r = row.get("representation") or {}
        if (
            r.get("id") == rep["id"]
            and str(r.get("version")) == str(rep["version"])
            and row.get("active", True)
        ):
            return row["uuid"]
    if not create:
        return None
    return g.call("POST", "/api/unprivileged_tools", json={"representation": rep})[
        "uuid"
    ]


def run_mode(g: Galaxy, uuid: str, history: str, mode: str) -> dict:
    res = g.call(
        "POST",
        "/api/tools",
        json={"history_id": history, "tool_uuid": uuid, "inputs": {"mode": mode}},
    )
    job_id = res["jobs"][0]["id"]
    out_id = res["outputs"][0]["id"]
    while True:
        job = g.call("GET", f"/api/jobs/{job_id}", params={"full": "true"})
        if job["state"] in ("ok", "error", "deleted", "failed", "skipped"):
            break
        time.sleep(20)
    metrics = {
        m["name"]: m.get("raw_value")
        for m in g.call("GET", f"/api/jobs/{job_id}/metrics") or []
    }
    out = g.call("GET", f"/api/datasets/{out_id}")
    content = ""
    if out.get("state") == "ok":
        content = g.s.get(
            f"{g.url}/api/datasets/{out_id}/display", timeout=120
        ).text.strip()
    return {
        "mode": mode,
        "job_id": job_id,
        "job_state": job["state"],
        "exit_code": job.get("exit_code"),
        "stdout": (job.get("tool_stdout") or job.get("stdout") or "").strip(),
        "stderr": (job.get("tool_stderr") or job.get("stderr") or "").strip(),
        "job_messages": job.get("job_messages"),
        "info": out.get("misc_info"),
        "metrics": {k: v for k, v in metrics.items() if k in METRICS},
        "output_state": out.get("state"),
        "output_content": content,
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--host", choices=sorted(HOSTS), required=True)
    ap.add_argument(
        "--modes", default="kill", help="comma-separated: oom-file, oom-pipe, kill"
    )
    ap.add_argument(
        "--deactivate",
        action="store_true",
        help="retire the registration instead of running",
    )
    ap.add_argument("--keep-history", action="store_true")
    ap.add_argument(
        "--yes", action="store_true", help="act; without it, only say what would happen"
    )
    args = ap.parse_args()

    rep = yaml.safe_load(TOOL.read_text())
    reg = Galaxy(REGISTRY.get(args.host, args.host))
    if args.deactivate:
        uuid = tool_uuid(reg, rep, create=False)
        print(f"{rep['id']} {rep['version']} on {reg.url}: {uuid or 'not registered'}")
        if uuid and args.yes:
            reg.call("DELETE", f"/api/unprivileged_tools/{uuid}")
            print("deactivated")
        return
    modes = [m for m in args.modes.split(",") if m]
    if not args.yes:
        print(
            f"would register {rep['id']} {rep['version']} on {reg.url} if absent, run {modes} on {args.host}"
        )
        return
    uuid = tool_uuid(reg, rep, create=True)
    g = Galaxy(args.host)
    history = g.call(
        "POST", "/api/histories", json={"name": "probe: BusyBox sort kill (delete me)"}
    )["id"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        for mode in modes:
            rec = {
                "host": args.host,
                "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tool": rep["version"],
            }
            rec.update(run_mode(g, uuid, history, mode))
            with OUT.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(json.dumps(rec, indent=1))
    finally:
        if not args.keep_history:
            g.call("DELETE", f"/api/histories/{history}", json={"purge": True})


if __name__ == "__main__":
    main()
