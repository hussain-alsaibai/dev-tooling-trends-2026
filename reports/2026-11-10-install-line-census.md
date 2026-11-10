# The install line is a claim, and none of the 54 held

**2026-11-10 · census of every `pip install` command in the `tiny-*` fleet**

Yesterday's report sampled the 25 packages advertised on more than one README.
This one does not sample. It extracts the install command from all 54 fleet
repos that have one, resolves the package name against the live PyPI index, and
asks a single question per repo:

> If a stranger runs the first command in your Install section, do they get
> your code?

The answer, this morning:

| Result | Repos |
|---|---|
| `pip install <name>` → **404**, package does not exist | **49** |
| `pip install <name>` → **200**, but the name belongs to **another maintainer** | **4** |
| `pip install <name>` → **200**, but it documents a *sibling* repo, not itself | **1** |
| `pip install <name>` → installs **our** code | **0** |
| **Total repos with a `pip install` line** | **54** |

Zero. Not one of the 54 installs the repo whose README it is. Every one of
those repositories has a green CI badge.

Four of the five `200` rows are the dangerous ones, because the command runs
cleanly and there is no error to notice.

## Method

The extraction is deliberately crude, because crude is reproducible:

```bash
for d in tiny-*/; do
  [ -f "$d/README.md" ] || continue
  grep -qE "pip install [a-z]" "$d/README.md" || continue
  pkg=$(grep -oE "pip install (git\+https://github.com/hussain-alsaibai/[a-z0-9._-]+\.git|[a-z0-9._-]+)" \
        "$d/README.md" | head -1 | sed 's|pip install ||; s|git+https://github.com/hussain-alsaibai/||; s|\.git||')
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$pkg/json" --max-time 8)
  printf "%s\t%s\t%s\n" "$d" "$pkg" "$code"
done
```

54 rows came out; 49 read `404` and 5 read `200`. The `200` rows are the
interesting ones, so each was checked for ownership:

```bash
curl -s "https://pypi.org/pypi/tiny-router/json" | python3 -c "import json,sys; print(json.load(sys.stdin)['info']['author'])"
```

| Name | Owner of the PyPI name | What it actually is ||---|---|---|
| `tiny-router` | Shiri Nekono | "Tiny HTTP router", 7 releases, `github.com/nekonoshiri/tiny-router` |
| `tiny-cli` | TinyBio LLC | "tinybio cli" — genomic tools in the cloud, 1 release |
| `tiny-eval` | (unset) | "TinyEval: A tiny evaluation framework for language models", 3 releases |
| `tiny-memo` | meng | "A memo/note-taking application with local storage and optional blockchain features", 6 releases |
| `tiny-mcp-skel` | *documents* `pip install tiny-router` | a skeleton repo whose Install section points at the router above, not at itself |

`tiny-cli` is the worst shape of this: a genomics CLI is a plausible thing to
find in a developer-tools context, so a user who follows our README gets a
working `pip install`, a working command, and the wrong program entirely. It
never errors. There is no point at which the mistake surfaces.

## Why the badges were green

Because CI tests the checkout, and the checkout is fine. The install line is a
claim about the *index*, and no step in any of these workflows ever asked the
index anything. This is the same shape as AGENTS.md's "a passing test file is
not proof if it never ran" — the artifact that would have caught it was never
built, so its absence read as success.

The 2026-11-09 entry in AGENTS.md already records this exact defect twice over:
"install command pointed at nothing" in `tiny-mcp-audit` (this repo, second
time) and the README `pip install` line. Two days later the census shows the
pattern is not an incident but the fleet default.

## What was actually fixed today

Two of the 49 were repaired, by pointing at the only path that works:
- **`tiny-mcp-audit`** — `026999a`. README install → repository URL. Verified in
  a clean venv: builds `tiny-mcp-audit==0.3.0` and imports.
- **`tiny-route-redact`** — `ead2186`. Also documented the dependency order,
  because `tiny-secret-mask` (its hard dependency) is a 404 too, so installing
  either one alone fails. Verified: `redact_path('/u/<uuid>')` →
  `/u/[REDACTED:uuid]`.

Both were checked by *running the command*, not by reading the diff. A `git+`
URL that 404s would have been a lateral move.

## What was not fixed, and why

Publishing 49 packages to PyPI is the right fix and it is blocked on a
credential that does not exist in this environment — `~/.pypirc` is absent, no
`TWINE_*` or PyPI token is in the environment. Writing the READMEs to say
"coming to PyPI soon" would be the warning-with-exit-0 pattern AGENTS.md bans:
it enforces nothing and reads like a fix.

So the honest state is: 47 repos still advertise an install that does not work
(49 minus the two repaired today), four advertise a command that installs a
stranger's package, and the fleet needs either a PyPI token or a decision to
stop claiming pip entirely and standardise on the `git+` form proven today.

## The rule

**A README install command is a factual claim about a third-party index, and it
must be resolved against that index in CI.** The check is one `curl` and a
status-code compare — cheaper than any test in these repos. `200` is not enough
either: compare the package's `project_url` or author against ours, because the
name may be taken by a maintainer whose package happens to be excellent, and
then neither the 404 nor the 200 tells you which one the user got.

The follow-on check, for anything that does publish: a CI job that installs the
*released* artifact in a clean venv and imports it. Until that exists, a green
badge means the source tree compiles, which was never the question.
