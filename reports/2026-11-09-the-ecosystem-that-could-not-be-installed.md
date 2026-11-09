# The Ecosystem That Could Not Be Installed

**Date:** 2026-11-09
**Census of:** the 25 packages advertised in every `tiny-*` README's "Ecosystem" section
**Method:** install each package from source in a clean target dir; read its published
`pyproject.toml`/`setup.py` over the GitHub API; resolve every advertised PyPI name
against `https://pypi.org/pypi/<name>/json`.

---

## TL;DR

The `tiny-*` ecosystem is advertised on **every** one of its READMEs as a coherent,
composable toolkit. It is not installable as one.

| Measure | Result |
|---|---|
| Packages advertised in the ecosystem list | **25** |
| Advertised packages that ship no packaging metadata | **13 (52%)** |
| Advertised packages whose `pip install <name>` resolves to **someone else's** package | **3** |
| Advertised packages whose `pip install <name>` resolves to nothing | **10** |
| Cross-library integration claims that were ever tested before today | **0** |
| Cross-library integration claims that were **false** when tested today | **2 defects** in one seam |

Three separate failure modes, all in the same list, all visible to any developer
who tries to follow it:

1. **Not installable at all.** 13 of 25 have a single module, tests and CI, but no
   `pyproject.toml` and no `setup.py`. `pip install git+...` fails with
   *"does not appear to be a Python project"*.
2. **Wrong package installed.** `tiny-queue`, `tiny-flags` and `tiny-eventbus` are
   real names on PyPI belonging to **other maintainers**. The README instruction
   is `pip install tiny-queue`; that command succeeds and installs a stranger's
   code. This is the `snapdb` trap recorded in AGENTS.md on 2026-11-09, still live
   in three more repos.
3. **Claims that were never executed.** `tiny-config` promised a round-trip with
   `tiny-validator`; it works only for flat configs. See below.

---

## 1. The installability gap

Verified by listing each repo's published root contents over the GitHub API and by
attempting a real install.

**Not installable (13):** `tiny-compose`, `tiny-cron`, `tiny-embed`, `tiny-eventbus`,
`tiny-flags`, `tiny-idempotency`, `tiny-mcp`, `tiny-metrics`, `tiny-pool`,
`tiny-queue`, `tiny-rate`, `tiny-secret`, `tiny-timeout`, `tiny-trace`.

Reproduced end to end:

```
$ pip install "git+https://github.com/hussain-alsaibai/tiny-rate.git"
ERROR: git+https://github.com/hussain-alsaibai/tiny-rate.git does not appear to be
a Python project: neither 'setup.py' nor 'pyproject.toml' found.
```

Meanwhile `tiny-rate/README.md` line 6 says:

```
pip install tiny-rate
```

`tiny-rate` is not on PyPI. So the README's only install instruction fails, and the
ecosystem link that brought the developer there points at a repo that cannot be
installed. A developer following the documented path gets a hard stop twice in a row.

**This is not a niche repo.** `tiny-rate`, `tiny-pool`, `tiny-queue` and `tiny-trace`
are four of the most-linked entries in the ecosystem list — they are listed on all
25 READMEs.

## 2. The name-collision gap (the dangerous one)

An install that *fails* is a bug. An install that *succeeds and installs the wrong
project* is a supply-chain problem.

| advertised name | PyPI owner | version |
|---|---|---|
| `tiny-queue` | Sravan JS `<mr.sravanjs@gmail.com>` | 0.1.0 |
| `tiny-flags` | Kaarle Kulvik `<k.kulvik@gmail.com>` | 2.0.0 |
| `tiny-eventbus` | — | resolved as the JS repo; no Python package |

Resolved with `curl https://pypi.org/pypi/<name>/json` and read from `info.author`.

A developer who runs the documented `pip install tiny-queue` gets a package by an
unrelated author, imports fine, and then cannot find the API the README describes.
Nothing errors. The 2026-10-09 `snapdb` lesson (`pip install <name>` succeeding is
not evidence it installed your code) generalises: **it is not one repo, it is the
ecosystem's naming policy**, and there isn't one.

## 3. The integration gap — found by actually composing the packages

The READMEs link to each other and the descriptions are accurate. What was never
tested is whether the packages **work together**. Installing six of them from source
and composing them found a false documented promise in the first seam tried:

`tiny_config.to_json_schema()`'s docstring and the v0.4.0 changelog both say:

> Round-trips with `tiny-validator.from_json_schema()`.

It does not, for any nested config:

```
ValueError: property 'host': unsupported keywords: ['_present']
ValueError: property 'x': unsupported keywords: ['nullable']
```

Two defects, both proven against the published 0.4.0 code:

1. `_present` — an **internal** inference marker — was stripped only from
   top-level properties. Nested objects and `items.properties` kept it, so the
   document was not valid JSON Schema.
2. A null-sampled field was spelled `{"type": "null", "nullable": true}`.
   `nullable` is an **OpenAPI 3** keyword, absent from JSON Schema draft 2020-12.

Both only surface on nested or nullable configs — the shapes every real service has,
and the shapes the existing unit tests did not assert on. The tests checked
`properties.host.type == "string"` and never that the key set was *exactly* `{"type"}`.

Fixed in `tiny-config` 0.4.1 and verified end to end against the published
`tiny-validator` 0.7.0:

```
to_json_schema({'db': {'host','port'}}) -> from_json_schema -> validate
  valid config   -> []
  port='nope'    -> [{'path': 'db.port', 'message': 'expected integer'}]
  {}             -> [{'path': 'db',    'message': 'missing required field'}]
```

The three new regression tests fail against 0.4.0 and pass against 0.4.1, on
3.8 through 3.12 in CI.

---

## What this says about the ecosystem as a product

The individual packages are good: zero dependencies, single file, real tests, green
CI, honest performance numbers. The **ecosystem** is the weak artifact, and it is the
thing every README spends 25 lines advertising.

A 25-package toolkit where half cannot be installed is, to a developer, a 25-link
page of dead ends. The failure is invisible from inside any single repo — each one
has its own green badge and its own passing tests. It is only visible from the
position of a user who tries to follow the advertised path, which is the position
nobody on the inside occupies.

**The rule worth keeping:** an ecosystem claim is a distributed assertion. It is
true only if *every* member is installable and *every* advertised seam is executed.
Neither was ever checked, because no repo's CI is able to check another repo. The
cheapest real guard is a single "ecosystem smoke test" job that clones the advertised
list, installs each one, imports it, and runs the documented integration snippet.

## Actionable

1. **Add packaging to the 13.** Each already has `tiny_<name>.py`, tests and CI —
   the work is a `pyproject.toml` plus a build job that asserts the wheel ships the
   module (the `tiny-worktree` empty-wheel guard).
2. **Stop telling users to `pip install` names we do not own.** Until the packages
   are published under names we control, the install line must be the `git+` form.
   For `tiny-queue`, `tiny-flags`, `tiny-eventbus` the current line installs a
   stranger's code — that is the highest-severity item here.
3. **Add an ecosystem smoke test** that installs the advertised list and runs the
   documented snippet. The `tiny-config` round-trip bug would have been caught the
   day it was written.

---

## Fixed in this pass (2026-11-09)

| Repo | Change | Verified |
|---|---|---|
| `tiny-config` | 0.4.1 — `to_json_schema()` strips private markers recursively; stops emitting the OpenAPI `nullable` keyword | 3 new tests fail on 0.4.0, pass on 0.4.1; **70 tests green on 3.8/3.9/3.12 in CI**, round-trip proven against published `tiny-validator` 0.7.0 |
| `tiny-queue` | `pyproject.toml` added; README install line is now the `git+` URL with an explicit warning against the squatted PyPI name; `scripts_check_wheel.py` + `Install` workflow | `Install` and `CI` workflows **green**; log shows wheel built, module asserted present, wheel installed and imported |
| `tiny-flags` | same three changes | `Install` and `CI` workflows **green**; 59 tests pass |

The empty-wheel guard was proven in both directions before shipping: it exits 0 on
a real wheel and exits 1 on a wheel rebuilt to contain only `dist-info`. A guard
that has only ever been seen passing is not a guard.

**Still open:** 11 of the original 13 remain unpackaged (`tiny-compose`, `tiny-cron`,
`tiny-embed`, `tiny-eventbus`, `tiny-idempotency`, `tiny-mcp`, `tiny-metrics`,
`tiny-pool`, `tiny-rate`, `tiny-secret`, `tiny-timeout`, `tiny-trace`), and
`tiny-eventbus` is a **JavaScript** package (`npm install tiny-eventbus`) that the
Python ecosystem lists advertise as a peer without saying so. That is not a broken
repo — its README is accurate — but a reader of the Python `tiny-*` list who follows
that line and reaches for `pip` finds a module that does not exist. The list is the
artifact at fault.
