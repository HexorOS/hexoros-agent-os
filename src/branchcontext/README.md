# BranchContext v0.1 — Fork, Explore, Commit

Speculative execution primitive for HexorOS agent workflows. An agent forks
its workspace into N isolated copy-on-write branches, explores each path in
parallel, and the **first branch to commit wins**. Losing branches are
discarded without ever touching the base state.

Based on Wang & Zheng (2026), *"Fork, Explore, Commit: Copy-on-Write State
Management for Agent Workflows"*.

## Why

Agents need to try things. Trying things on live state corrupts it. Classic
sandboxes give you isolation but no cheap way to *promote* a successful
exploration back to the real workspace. BranchContext gives agents a
git-like lifecycle for their entire working state:

```
fork(n) ──> explore in parallel ──> first commit wins ──> losers discarded
```

## Usage

```python
from branchcontext import BranchContext, StaleBranchError

with BranchContext("/path/to/workspace") as ctx:
    a = ctx.fork("strategy-a")
    b = ctx.fork("strategy-b")

    a.run(lambda p: try_strategy_a(p))   # p = isolated Path
    b.run(lambda p: try_strategy_b(p))

    a.commit()      # base workspace fast-forwards to a's state
    b.commit()      # raises StaleBranchError -> b.abort()
```

Demo: `python3 examples/branchcontext_demo.py`

## Guarantees (v0.1)

- **Isolation** — every branch gets its own worktree; explorations never
  see each other or the base.
- **Atomic promotion** — commit is fast-forward-only under an exclusive
  lock; the base moves exactly once per generation.
- **First-commit-wins** — safe under multi-threaded exploration; losers
  get `StaleBranchError` and can be aborted cleanly.
- **Clean failure** — aborted/lost branches leave zero trace in the base.
- **Any directory** — non-git workspaces get an ephemeral shadow repo,
  removed on `close()`.

## Status & roadmap

| Layer | Status |
|---|---|
| Fork-explore-commit lifecycle, first-commit-wins | ✅ v0.1 (this module) |
| CoW backend: git worktrees (userspace, no root) | ✅ v0.1 |
| Branch-aware inter-agent message bus (branch IDs) | 🔜 planned |
| BranchFS: FUSE-based CoW filesystem backend | 🔜 planned |
| Kernel-level integration (eBPF resource control, AgentCgroup) | 🔭 research track |

v0.1 is a deliberately small, dependency-free (stdlib + git) userspace
implementation. The API is designed so backends (git → BranchFS → kernel)
can be swapped without changing agent code.
