# Report — the install line is the contract, and 85 of our names are free

**Date:** 2026-11-11 · **Scope:** 93 packages across this workspace and
`repos/` · **Tooling:** `audit_pypi_names.py` (stdlib only, shipped with this
report)

---

## TL;DR

1. **85 of 93 package names are unclaimed on PyPI.** Not "we could publish
   eventually" — *the name is free right now*. For most of those repos the
   README contradicts that: it says "not yet on PyPI" and sends people to a
   `git+https://` URL that pip has to clone and build.
2. **The one package that *is* published with our name is six minor versions
   behind.** `pysnapdb` is on PyPI at 0.14.0; the repo is at 0.18.1 as of
   today. Nobody noticed, because the version badge in the README is not read
   by anything.
3. **7 names are collisions, and 3 of those READMEs are correctly honest.**
   `tiny-cli`, `tiny-router`, `tiny-eval`, `tiny-memo` already say "this name
   belongs to someone else, use the git URL". `tiny-diff` has the same
   collision and **no install section at all** — it shows `pip install`
   nowhere, so a first-time reader is left guessing rather than misled.
   `joblib` and `xvfbwrapper` are vendored working copies, not our projects.
4. **The audit tool itself refuses to call HTTP 200 a pass.** That was the
   2026-11-09 failure: four collisions read as "published" because the name
   existed. The classifier now requires the PyPI project URL or author email
   to name `hussain-alsaibai`, and it exits `2` — not `0` — when the network
   fails, so a dead connection cannot look like a clean report.

---

## The classification

| status | count | meaning |
|---|---:|---|
| `free` | 85 | name available; nothing to install |
| `collision` | 7 | someone else owns the name; `pip install X` fetches their code |
| `ours` | 1 | `pysnapdb` — right package, stale version |
| `error` | 0 | every request resolved |

The 7 collisions, classified by owner rather than by status code:

| name | PyPI says | our position |
|---|---|---|
| `tiny-cli` | 0.1.0, TinyBio LLC (genomics CLI) | README honest, uses git URL |
| `tiny-router` | 0.0.8, Shiri Nekono | README honest, uses git URL |
| `tiny-eval` | 0.5.0 | README honest, uses git URL |
| `tiny-memo` | 1.1.6, "meng" | README honest, uses git URL |
| `tiny-diff` | 0.1.0 | **no install section at all** |
| `joblib` | 1.6.0 (upstream) | vendored copy, not a project of ours |
| `xvfbwrapper` | 0.2.37 (Corey Goldberg) | vendored copy, not a project of ours |

`tiny-diff` is the only real gap in this table, and it is a documentation gap
rather than a false claim: the README opens with "zero dependency, one file"
and never tells you how to get the file.

---

## Why a free name is worth more than a README badge

The install path is the only part of a README a user executes. Everything
else — the API table, the benchmark, the "why?" section — is read *after* the
install either works or doesn't.

Eight of our repos tell the reader to install from a `git+https://` URL
because the name was taken at the time the README was written. Each of those
is now a slower, noisier first run than it needs to be (`pip install
git+https://...` clones and builds; `pip install tiny-x` downloads a wheel).
For the 85 free names, publishing is a one-line change in the README plus a
release, and the name is gone the moment somebody else claims it — PyPI names
are first-come and the `tiny-*` prefix is popular (35 of the 93 names are
already in someone's hands or ours).

## What I would fix, in order

1. **`pysnapdb` 0.14.0 → 0.18.1.** Largest real user impact: a published
   package six releases behind its repo, including today's packaging fix.
2. **`tiny-diff` install section.** One paragraph; no false claim is currently
   made, but a reader has no entry point.
3. **Publish from the free list, highest-adoption first.** The candidates with
   real prior work and a free name: `tiny-audit` (0.2.0 today),
   `tiny-semaphore`, `tiny-json`, `tiny-memory`, `tiny-retry`,
   `tiny-checkpoint`, `tiny-inspector`. Publishing needs a PyPI token, which
   this job does not have — the README and the tool are ready, the credential
   is the blocker.

## The tool

```bash
python3 audit_pypi_names.py audit_work/names.tsv --json audit_work/result.json
```

TSV of `repo_dir<TAB>pypi_name`. Exit `0` clean, `1` any collision, `2` the
audit could not complete. The `2` matters: an audit that reports "all fine"
when PyPI is unreachable is worse than no audit, because it converts a
network problem into a false assurance about published state.
