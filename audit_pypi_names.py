#!/usr/bin/env python3
"""audit_pypi_names.py — check whether the name a README tells you to install
actually installs *this* project.

    python3 audit_pypi_names.py audit_work/names.tsv
    python3 audit_pypi_names.py audit_work/names.tsv --json out.json

Input is tab-separated: ``repo_dir<TAB>pypi_name``. One line per package.

Why this exists
---------------
On 2026-11-09 an install-line census of this fleet found 49 of 54 install
lines were wrong. Four of them looked fine because the *name* existed on PyPI
and returned HTTP 200 — they were other maintainers' packages:

    tiny-cli   -> 200, "TinyBio LLC",  a genomics CLI
    tiny-router-> 200, "Shiri Nekono", a different router
    tiny-log   -> 200, someone else's logger
    ...

So a 200 is not a pass. The only pass is:

    the name exists  AND  (the project URL points at our repo
                           OR the author email is ours)

Anything else is a collision and needs the README install line removed or
replaced with a git+https URL. Exit code is 0 for a clean report, 1 when any
name collides, 2 when the *audit* itself could not complete (network, bad
input) — because a check that silently reports "all fine" on a network error
is worse than no check.

Stdlib only. No dependencies, no credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

OWNER = "hussain-alsaibai"
OWNER_EMAIL = "hussain.alsaibai@gmail.com"
TIMEOUT = 15

STATUS = {
    "free": "name is available on PyPI (nothing to install yet)",
    "ours": "name resolves to this project — the install line is honest",
    "collision": "name belongs to someone else — the install line is a bug",
    "error": "could not determine; do not read this as a pass",
}


def fetch(name: str) -> tuple[int, dict | None]:
    url = f"https://pypi.org/pypi/{name}/json"
    request = urllib.request.Request(url, headers={"User-Agent": "pypi-name-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 404, None
        return exc.code, None
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  ! network: {name}: {exc}", file=sys.stderr)
        return 0, None


def classify(name: str) -> dict:
    status, payload = fetch(name)
    if status == 404:
        return {"name": name, "status": "free", "detail": ""}
    if not payload:
        return {"name": name, "status": "error", "detail": f"HTTP {status}"}

    info = payload.get("info") or {}
    urls = info.get("project_urls") or {}
    surface = " ".join(
        str(v) for v in [
            info.get("home_page"),
            info.get("author_email"),
            info.get("author"),
            info.get("maintainer_email"),
            info.get("maintainer"),
            *urls.values(),
        ] if v
    ).lower()

    ours = (OWNER in surface) or (OWNER_EMAIL in surface)
    return {
        "name": name,
        "status": "ours" if ours else "collision",
        "detail": f"{info.get('version')} by {info.get('author') or info.get('maintainer') or '?'}",
        "version": info.get("version"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", help="TSV: repo_dir<TAB>pypi_name")
    parser.add_argument("--json", help="write machine-readable results here")
    args = parser.parse_args(argv)

    rows = []
    with open(args.manifest, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            repo, _, name = line.partition("\t")
            if not name:
                print(f"bad manifest line: {line!r}", file=sys.stderr)
                return 2
            result = classify(name.strip())
            result["repo"] = repo.strip()
            rows.append(result)
            print(f"{result['status']:>9}  {name:<24} {result['detail']}")

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    print()
    for key in ("ours", "collision", "free", "error"):
        if counts.get(key):
            print(f"{counts[key]:>3}  {key:<10} {STATUS[key]}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"counts": counts, "rows": rows}, handle, indent=1)

    if counts.get("error"):
        return 2
    return 1 if counts.get("collision") else 0


if __name__ == "__main__":
    raise SystemExit(main())
