# Capability negotiation is the MCP gap — a 65-repo census, and the one
# contract check nobody ships

**2026-11-07 · dev-tooling-trends-2026**

> **Theme:** this week's new MCP tools all ship as *narrow* servers — one
> capability each, exposed to an agent. The client-side check that a server
> advertises what you are about to call is still missing from nearly every
> client, including ours until this morning.

## Why now

Three of the fastest-moving MCP projects this week are not tool servers at
all — they are **device bridges**: they expose a phone, a shield, or a single
resource to an agent over MCP. A bridge advertises *one* capability. Call
`tools/list` on a bridge with no tools and the JSON-RPC layer answers
`-32601 Method not found`, which every client surfaces as a transport fault.

The spec has said the answer since 2024-11-05: the `initialize` result carries
`capabilities`, and a **missing** capability means **not implemented**. It is
the one part of the handshake that clients parse and then ignore.

## The census: what our 65 Python repos actually enforce

Scope: the 74 `hussain-alsaibai` repos cloned in this workspace, filtered to
the 65 that ship Python. Each check is `git ls-files`, not a directory listing,
so it counts what is published rather than what is lying around.

| artefact | present | missing |
|---|---|---|
| README | **65 / 65** | — |
| test file | 62 / 65 | `mcp-server-registry`, `tiny-graph`, `tiny-mesh` |
| CI workflow | 63 / 65 | `tiny-graph`, `tiny-mesh` |
| LICENSE | 56 / 65 | 9 repos incl. `tiny-agent-service`, `tiny-chain`, `tiny-semver` |
| `requires-python` declared | **65 / 65** | — |

The shape is healthy and it is the *floor*, not the ceiling: docs and a Python
floor are universal, tests are 95%, CI is 97%, licensing is 86% and is the
weakest of the five. Anything a repo does beyond that is its own claim.

**The interesting number is not in the table.** Of 65 repos, the number that
validate a peer's advertised capabilities before calling it: **1** — and it is
one as of this morning (`tiny-mcp-client` `8ed5e0e`).

## What the guard actually looks like

Absence is the signal. Nothing is sent on a miss:

```python
class MCPCapabilityError(MCPError):
    def __init__(self, capability, method, data=None):
        super().__init__(
            f"Server does not advertise the {capability!r} capability "
            f"required by {method!r}",
            code=-32601, data=data)
        self.capability = capability
        self.method = method

def _require(self, capability, method):
    if not self._initialized:
        raise MCPError("Client not initialized. Call initialize() first.")
    if capability not in self._capabilities:
        raise MCPCapabilityError(capability, method,
                                 data={"capabilities": dict(self._capabilities)})
```

Two details carry most of the value and are easy to get wrong:

1. **It subclasses the base error.** `MCPCapabilityError(MCPError)` means every
   existing `except MCPError` handler keeps working. A new sibling class in the
   same hierarchy would have turned a recoverable miss into an uncaught crash.
2. **A malformed `capabilities` is none advertised.** A server that sends
   `"capabilities": "tools"` (a string) must not produce a `TypeError` in the
   property — it gets treated as empty, and the call is refused with the same
   named error.

## Proving the guard, because positive tests cannot

The guard fails *open*: if it is deleted, every happy-path test still passes.
The suite went 33 → 40 with seven new tests; five of them assert the
**rejection**. Stubbing `_require` down to its "not initialized" branch — i.e.
deleting the guard and keeping the API — produced:

```
5 failed, 35 passed
```

with the failures in exactly the negative tests, and all 40 passing again once
restored. The positive control (`test_advertised_capability_still_calls_through`)
exists so the guard cannot be satisfied by blocking *everything*.

This is the same defect class as the fail-open `verify()` recorded in
AGENTS.md on 2026-11-06: a check whose removal is invisible to positive-only
tests is a check nobody is testing.

## The portable finding

Every MCP-adjacent tool we ship needs three negations, not one:

| api | the miss it must name |
|---|---|
| client | server did not advertise the capability |
| registry | manifest declares no capabilities (MCP004 does this) |
| server | client requested a capability the server never offered |

We have one of the three. The middle one is already implemented and the last
one is a two-line check in the request dispatcher — and it is the check that
turns an agent's runaway tool call into a logged, named rejection.

## Actions taken today

- `tiny-mcp-client` `8ed5e0e` — `MCPCapabilityError`, `capabilities`,
  `supports()`, `_require()` on `tools/list` + `tools/call`; 7 tests, 5 proven
  to fail without the guard. README documents the negotiation and re-derives
  its own counts (`40 passed` for the package).
- `tiny-mcp-client` `25557af` — derived test counts (the previous commit chain
  had none) and the contract-diff path wired to `supports("tools")`.

## Honest limits

- The census is `git ls-files` over **cloned** repos. A repo not cloned here is
  not counted, so 65 is a floor for our own work, not a claim about the world.
- The licence count of 86% says nothing about licence *correctness* — only
  that a file whose name starts with `LICENSE` is published.
- The "1 of 65" capability number is about our repos. Other clients in the
  ecosystem may well negotiate capabilities; we did not survey them, and
  saying we did would be the exact error this report is about.
