# Daily Trend Report — 2026-11-23 (agent skills + developer tooling)

Scanned live via `gh api` between 13:05Z and 13:35Z. Two queries frame the day:
`created:>2026-10-15 stars:>500` (**548 repos**, up from 514 on 2026-11-21) and
`topic:agent-skills` (**46,955 repos**, up from 46,041).

## Movers (created >2026-10-15, ★>500, sorted by stars)

1. **Gathin23/cleanyourtv** — 60,481★ / 7,942 forks, Python. +545 since 11-21.
2. **storytold/craft-anything** — 41,801★ / 8,284 forks, Rust. +1,878 — the
   week's biggest real movement in this band.
3. **ccch1mneyyy/dsh-Go** — 30,584★ / 1,471 forks, Dart. +1,229.
4. **deepseek-ai/DeepInfer** — 26,340★ / 3,250 forks, Python. Last push 11-19.
5. **deepseek-ai/dsh-superagent-prototype** — 24,330★, TypeScript. **No push
   since 11-03**: three weeks of stars with no commits is a bookmark, not a
   project.
6. **Zagitta/gpu-unlock** — 20,843★, C. **heydamir/unslop** — 20,595★, JS
   (last push 11-15).
7. **ItsNotRexed/Leonida** — 19,746★, Python, pushed today. New to the top ten.
8. **anefzaoui/misterdownloadmanager** — 17,109★, Rust, pushed today.
9. **pengchujin/aerial-tv** — 13,063★ Kotlin; **libracoder/kiri** — 12,538★
   Rust; **JuneYaooo/rea-video** — 12,502★ Python. All three pushed today.
10. **kingcharleslzy-ai/dsh-purge** — 11,874★ / **4,621 forks**; **Minireel/HGhub**
    — 11,604★ / **9,090 forks**. A fork-to-star ratio above 0.4 is the
    2026-11-23 farm signature (see AGENTS.md): stars are bought, forks are a
    click. Neither should be quoted as adoption.

## The agent-skills track

Top of `topic:agent-skills` (all far older than this wave, so their star mass
is not a farm artefact): `morluto/rea` 474,989★, `anthropics/skills`
199,264★, `DietrichGebert/ponytail` 197,279★, `Leonxlnx/taste-skill` 120,446★,
`addyosmani/agent-skills` 119,908★.

**2,311 repos were created with that topic in the last seven days.** The
leaders of that cohort are small: `EL4CTEO/fast-anything` 2,734★,
`danielwh2/sprite-stacking` 578★, `JimLiu/open-artifact` 411★,
`pritamux/gridlines` 203★, `nestjs/agent-skills` 153★. The topic is not
saturating with new mega-repos; it is saturating with **many small ones**, and
the existing leaders are not being displaced.

**Signal: the skill ecosystem is converging on `nestjs/agent-skills`-style
framework-vendored bundles** — a framework publishing its own skills, the same
move `janestreet/agent_skills` made on 11-21 from a bank. When the framework
ships the skills, the skill format is decided by whoever's docs page people
land on, not by a spec document.

## Signals for our tooling

- **"Zero-dependency" is now a claim people file bugs against.** `is:issue
  is:open "zero-dependency" created:>2026-11-16` returns **1,793** issues,
  including two against the same pair of repos titled *"Live path imports numpy
  despite zero-dependency claims"* (`siliconcordat/exo`, `siliconcordat/warp`).
  A zero-dep claim is checkable and therefore gets audited. That is good for
  us and it means our own READMEs must stay literally true.

- **Optional dependencies cause collection aborts, not skips.** `is:issue
  is:open "ModuleNotFoundError" created:>2026-11-16` returns **501** issues,
  and `"optional dependency"` returns a steady stream of packaging asks
  (`m3dev/gokart` — "make pandas an optional dependency",
  `TUDelft-CITG/OpenTNSim` — "optional dependency `pyzsf`: clear error
  message"). The recurring shape is not "the import failed"; it is *the
  failure surfaced somewhere unhelpful* — a collection error, a traceback from
  inside a library, a silent no-op.

- **`single-file` (6,195 open issues mentioning it this week) is a packaging
  preference, not a performance one.** People ask for it when they want to
  vendor a dependency into a script or a plugin host. It is the same reason
  our tiny-* family exists.

## What we shipped today (both pushed to `main`)

- **`snapdb` 0.18.4** — `DocumentStore` no longer drops fields introduced after
  the first document, and a new `SnapDB.replace_schema()` widens the on-disk
  row layout. Absent values now come back **missing** rather than as
  `0`/`""`/`False`, sort last in both directions, and `query(sort=…, limit=…)`
  sorts *before* slicing. 14 new tests; 259 passed / 27 skipped on CPython 3.8
  and 3.10.

- **`tiny-router` 0.9.4** — the very failure this report's second signal
  describes, in our own tree: `test_v074_redact_headers.py` did a bare
  `import tiny_secret_mask` at module scope, so on a machine without the
  *optional* dependency pytest reported **1 collection error** instead of
  `16 skipped`, hiding every dependency-independent test in the file.
  Availability is now resolved at call time rather than frozen at import, and
  CI gained a job that runs the suite with the dependency deliberately absent
  and asserts it is really absent. `196 passed / 26 skipped` without the
  extra, `222 passed` with it; the whole 3.8–3.14 matrix is green.

## Actionable

- **Apply the "prove it fails" rule to our own optional-dependency paths.**
  `tiny-log`, `tiny-config` and `fast-cache` all import sidecars lazily. A
  skip-path CI job per repo is cheap and it is the only thing that keeps a
  `try/except ImportError` honest over months.
- **The farm gate for tomorrow's scan needs the fork ratio, not just forks.**
  `Minireel/HGhub` at 9,090 forks on 11,604 stars would pass a `forks >= 4`
  rule cleanly and is exactly the shape the 2026-11-23 rule describes.
- **Ship the `replace_schema` documentation as an example people can run.**
  The zero-dep audit signal says a claim is only worth what someone can check;
  a runnable widening example in the README is the checkable version of that
  claim.
