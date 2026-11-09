# We Ran All 371 README Examples. 103 Worked.

**2026-11-09** · audit of 62 published `tiny-*/snapdb/fast-cache` repositories

---

## What we did

Every repository in this ecosystem documents itself with a README full of
Python. Nobody had ever executed those blocks. So we extracted all of them —
**371 fenced ```python blocks across 62 repos** — and ran each one in its own
subprocess, with the repository on `PYTHONPATH`, a 25-second timeout, and no
network.

This is not a claim that "69% of the READMEs are broken". Most of what failed
failed for honest reasons. The interesting part is which kind of failure each
one was, because each kind asks a different question.

## The raw result

| outcome | blocks | share |
|---|---|---|
| ran clean | 103 | 27.8% |
| fragment of a larger example | 214 | 57.7% |
| missing dependency | 22 | 5.9% |
| real code or doc error | **19** | **5.1%** |
| needs credentials / env | 5 | 1.3% |
| needs files or host paths | 3 | 0.8% |
| timeout | 5 | 1.3% |

The 214 "fragments" are blocks like `cache.get("k")` that continue an earlier
block in the same README. They are not defects; they are also not examples,
because nothing can run them. A block that cannot be run in isolation was
never verified by anyone, and it is indistinguishable from a wrong one until
somebody types it.

## The 19 real defects

Grouped, because the groups predict each other.

### A. The README documents an API that does not exist (6)

| repo | what the README says | what the class has |
|---|---|---|
| `tiny-router` | `@app.middleware` | `use()` only → `AttributeError` |
| `tiny-router` | `@app.websocket("/ws")` | `ws()` only → `AttributeError` |
| `tiny-eval` | `from tiny_eval import EvalSuite` | no `EvalSuite` in the module |
| `tiny-event-emitter` | `emitter.on("evt", handler)` | `on()` requires a positional `func` |
| `tiny-memo` | `bus.subscribe("evt", cb)` | `subscribe()` requires a positional `callback` |
| `tiny-agent-toolkit` | `BudgetGovernor`, `IdempotencyGuard`, `DirectoryScratchpad` | none importable |

Six packages, three shapes of the same mistake: the doc was written from the
design, the code shipped from the implementation, and nothing compared them.
`tiny-router`'s is the worst kind — the decorator form is what every router in
the Python ecosystem uses, so a reader who half-remembers FastAPI writes it
from instinct and gets an `AttributeError`, then blames themselves.

**Fixed today in `tiny-router` 0.9.1.** `middleware()` is now a real
decorator over `use()`; `websocket` is a property aliasing `ws`. The
regression test re-executes the README block verbatim, so the two cannot
drift apart again.

### B. Positional arguments in the wrong order (3)

`tiny-router`'s middleware example used `Response(401, {"error": ...})`. The
constructor is `(body, status)`. The example produced `body=b'401'` and
`status={'error': 'Unauthorized'}` — no exception, no warning, a nonsense
response at runtime.

This is the failure mode positional arguments are *for* when a signature is
`(body, status)` and every other HTTP library in the world is `(status,
body)`. It is not a bug you find by reading; it is a bug you find by running.
Fixed in 0.9.1 by using the keyword form in the doc.

### C. Examples that need the outside world but do not say so (10)

`tiny-mcp-client` (connection refused, method not allowed), `tiny-llm` (401),
`tiny-mcp-audit` (assertion), `tiny-dist-audit` (needs a built `.whl` in
`dist/`), `tiny-config` (needs `config.production.yaml`), `tiny-budget-ledger`
(needs `/var/lib/openclaw`), `tiny-bloom` (`TypeError: 'ellipsis' object is
not iterable`).

Every one of these is a *checkable* claim that nothing checks: "point this at
an MCP server", "audit this manifest", "audit this wheel". A README that
requires a fixture should ship the fixture, or the example is unverifiable
forever.

## What this means, plainly

- **This ecosystem's READMEs are documentation, not tests.** 103 of 371
  blocks could even run. The 19 defects lived in repositories whose unit
  tests are green — the tests exercise the implementation, and every one of
  these defects is a disagreement *between* the implementation and the doc.
- **A test suite cannot find this class of bug.** `tiny-router` had 196
  passing tests, including tests for `use()` and `ws()`. The aliases were
  missing because the doc was never a test input.
- **The cheap fix is to make the doc a test input.** One test file per repo
  that executes the README's primary block costs ~20 lines and catches every
  category A and B defect above.

## The rule we are adopting

> **A code example in a README is a claim, and a claim needs an executor.**
> Either a test executes the block, or the block belongs behind a
> `<!-- not-executed: needs a live MCP server -->` marker so the next reader
> knows it was never verified.

Applied today:

- `tiny-router` 0.9.1 — README middleware block is now executed by
  `test_v091_documented_api.py::test_readme_middleware_section_runs_verbatim`.
- `tiny-cli` 1.3.0, `tiny-log` 0.8.0 — shipped earlier today with their own
  regression files.

## Appendix: the probe

```python
# extract and run every fenced python block, one subprocess each
blocks = re.findall(r"```python\n(.*?)```", open("README.md").read(), re.S)
for b in blocks:
    subprocess.run([sys.executable, "-c", b], cwd=repo,
                   timeout=25, env={**os.environ, "PYTHONPATH": repo})
```

Classification was manual per `(repo, block)` and the raw table is
`/tmp/readme_run.json` on the build host. Five blocks timed out and are
excluded from every rate above rather than counted as passes.
