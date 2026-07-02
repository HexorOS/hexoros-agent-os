#!/usr/bin/env python3
"""BranchContext v0.1 demo — speculative execution with first-commit-wins.

Scenario: an agent must optimize a config file. It doesn't know which of
three strategies works, so it forks the workspace, explores all three in
parallel, and commits the first one that passes validation. Losing
branches are discarded; the base workspace never sees a broken state.

Run:  python3 examples/branchcontext_demo.py
"""

import json
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from branchcontext import BranchContext, StaleBranchError  # noqa: E402


def make_workspace() -> Path:
    ws = Path(tempfile.mkdtemp(prefix="agent-ws-"))
    (ws / "config.json").write_text(json.dumps({"batch_size": 1, "workers": 1}))
    (ws / "notes.md").write_text("# Agent workspace\n")
    return ws


def strategy(name: str, params: dict, cost_s: float):
    """Simulated exploration: each strategy takes different time and
    produces a different candidate config."""
    def explore(path: Path):
        time.sleep(cost_s)  # simulated LLM/tool-call latency
        cfg = json.loads((path / "config.json").read_text())
        cfg.update(params)
        (path / "config.json").write_text(json.dumps(cfg, indent=2))
        (path / "notes.md").write_text(f"# Optimized by {name}\n")
        return cfg
    return explore


def main():
    ws = make_workspace()
    print(f"base workspace: {ws}")
    print(f"base config:    {(ws / 'config.json').read_text()}\n")

    with BranchContext(ws) as ctx:
        specs = [
            ("conservative", {"batch_size": 4,  "workers": 2},  1.2),
            ("balanced",     {"batch_size": 16, "workers": 4},  0.4),
            ("aggressive",   {"batch_size": 64, "workers": 16}, 0.8),
        ]
        branches = {name: ctx.fork(name) for name, _, _ in specs}
        print(f"forked {len(branches)} speculative branches:")
        for b in branches.values():
            print(f"  [{b.branch_id}] {b.name} -> {b.path.name}")
        print()

        def explore_and_commit(name, params, cost):
            branch = branches[name]
            result = branch.run(strategy(name, params, cost))
            try:
                ref = branch.commit(f"strategy '{name}' validated")
                return name, "COMMITTED", ref[:8], result
            except StaleBranchError:
                branch.abort()
                return name, "discarded (stale)", "-", result

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(explore_and_commit, *s) for s in specs]
            for f in futures:
                name, status, ref, cfg = f.result()
                print(f"  {name:<14} {status:<18} ref={ref}  cfg={cfg}")

        print(f"\nwinner: {ctx.winner} (first-commit-wins)")

    final = json.loads((ws / "config.json").read_text())
    notes = (ws / "notes.md").read_text().strip()
    print(f"final config:   {final}")
    print(f"final notes:    {notes!r}")
    assert notes == "# Optimized by balanced", "expected fastest branch to win"
    print("\nOK — base state updated exactly once, losers left no trace.")


if __name__ == "__main__":
    main()
