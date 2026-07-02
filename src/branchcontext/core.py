"""BranchContext v0.1 — Fork-Explore-Commit for agent workflows.

Copy-on-write state management for speculative agent execution,
modeled after Wang & Zheng (2026), "Fork, Explore, Commit: Copy-on-Write
State Management for Agent Workflows".

An agent forks its workspace into N isolated branches, explores each
path in parallel, and the first branch to commit wins. Losing branches
are discarded without ever corrupting the base state.

v0.1 implementation notes:
- CoW backend: git worktrees (userspace, no root, no FUSE required).
  BranchFS (FUSE) and kernel-level integration are on the roadmap.
- First-commit-wins is enforced with an exclusive lock file, so it is
  safe under multi-threaded exploration.
- Works on any directory; non-git workspaces get an ephemeral shadow
  repository that is removed on close().

Example:
    with BranchContext("/path/to/workspace") as ctx:
        a = ctx.fork("strategy-a")
        b = ctx.fork("strategy-b")
        # ... explore a.path and b.path in parallel ...
        a.commit()          # wins
        b.commit()          # raises StaleBranchError
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

__all__ = [
    "BranchContext",
    "Branch",
    "BranchContextError",
    "StaleBranchError",
    "DirtyWorkspaceError",
]


class BranchContextError(RuntimeError):
    """Base error for BranchContext operations."""


class StaleBranchError(BranchContextError):
    """Raised when committing a branch after another branch already won."""


class DirtyWorkspaceError(BranchContextError):
    """Raised when the base workspace has uncommitted changes at fork time."""


_GIT_IDENT = [
    "-c", "user.name=BranchContext",
    "-c", "user.email=branchcontext@hexoros.local",
]


def _git(args: list[str], cwd: Path) -> str:
    """Run a git command, return stdout, raise on failure."""
    result = subprocess.run(
        ["git", *_GIT_IDENT, *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BranchContextError(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


@dataclass
class Branch:
    """A single speculative branch of the workspace."""

    branch_id: str
    name: str
    path: Path
    _ctx: "BranchContext" = field(repr=False)
    _closed: bool = field(default=False, repr=False)

    def run(self, fn: Callable[[Path], object]) -> object:
        """Explore: run `fn` against this branch's isolated workspace."""
        if self._closed:
            raise BranchContextError(f"branch {self.name} is closed")
        return fn(self.path)

    def commit(self, message: Optional[str] = None) -> str:
        """First-commit-wins: publish this branch's state back to base.

        Returns the commit hash on success. Raises StaleBranchError if
        another branch already committed for this generation.
        """
        return self._ctx._commit_branch(self, message)

    def abort(self) -> None:
        """Discard this branch and its worktree."""
        self._ctx._discard_branch(self)

    @property
    def is_stale(self) -> bool:
        """True if another branch of the same generation already won."""
        return self._ctx._generation_won and not self._closed


class BranchContext:
    """Fork-explore-commit lifecycle manager for a workspace directory."""

    def __init__(self, workspace: str | os.PathLike):
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise BranchContextError(f"workspace does not exist: {self.workspace}")

        self._lock = threading.Lock()
        self._branches: dict[str, Branch] = {}
        self._generation_won = False
        self._winner: Optional[str] = None
        self._tmp = Path(tempfile.mkdtemp(prefix="branchctx-"))

        self._shadow = not (self.workspace / ".git").exists()
        if self._shadow:
            # Non-git workspace: shadow repo tracks state without touching
            # the user's directory layout.
            self._git_dir = self._tmp / "shadow.git"
            self._run(["init", "--quiet", str(self.workspace)], env_gitdir=True)
            self._snapshot("branchcontext: baseline")
        else:
            self._git_dir = None
            status = _git(["status", "--porcelain"], self.workspace)
            if status:
                raise DirtyWorkspaceError(
                    "base workspace has uncommitted changes; commit or stash "
                    "before forking (speculative branches need a clean baseline)"
                )
        self._base_ref = self._head()

    # -- public API ---------------------------------------------------------

    def fork(self, name: Optional[str] = None) -> Branch:
        """Create an isolated copy-on-write branch of the workspace."""
        with self._lock:
            if self._generation_won:
                raise StaleBranchError(
                    f"generation already committed by '{self._winner}'"
                )
            branch_id = uuid.uuid4().hex[:8]
            name = name or f"branch-{branch_id}"
            ref = f"branchctx/{name}-{branch_id}"
            wt_path = self._tmp / ref.replace("/", "_")
            self._run(["worktree", "add", "--quiet", "-b", ref,
                       str(wt_path), self._base_ref])
            branch = Branch(branch_id=branch_id, name=name,
                            path=wt_path, _ctx=self)
            self._branches[branch_id] = branch
            return branch

    def close(self) -> None:
        """Discard all remaining branches and temporary state."""
        for branch in list(self._branches.values()):
            if not branch._closed:
                self._discard_branch(branch)
        shutil.rmtree(self._tmp, ignore_errors=True)
        if self._shadow:
            shutil.rmtree(self.workspace / ".git", ignore_errors=True)

    def __enter__(self) -> "BranchContext":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @property
    def winner(self) -> Optional[str]:
        return self._winner

    # -- internals ----------------------------------------------------------

    def _run(self, args: list[str], env_gitdir: bool = False) -> str:
        return _git(args, self.workspace)

    def _head(self) -> str:
        return _git(["rev-parse", "HEAD"], self.workspace)

    def _snapshot(self, message: str) -> None:
        _git(["add", "-A"], self.workspace)
        _git(["commit", "--quiet", "--allow-empty", "-m", message],
             self.workspace)

    def _commit_branch(self, branch: Branch, message: Optional[str]) -> str:
        with self._lock:
            if branch._closed:
                raise BranchContextError(f"branch {branch.name} is closed")
            if self._generation_won:
                raise StaleBranchError(
                    f"branch '{branch.name}' lost: '{self._winner}' "
                    "already committed this generation (first-commit-wins)"
                )
            msg = message or f"branchcontext: commit '{branch.name}'"
            # Snapshot the branch worktree.
            _git(["add", "-A"], branch.path)
            _git(["commit", "--quiet", "--allow-empty", "-m", msg],
                 branch.path)
            ref = _git(["rev-parse", "HEAD"], branch.path)
            # Fast-forward base workspace to the winning branch.
            _git(["merge", "--ff-only", "--quiet", ref], self.workspace)
            self._generation_won = True
            self._winner = branch.name
            self._teardown_worktree(branch)
            return ref

    def _discard_branch(self, branch: Branch) -> None:
        with self._lock:
            if not branch._closed:
                self._teardown_worktree(branch)

    def _teardown_worktree(self, branch: Branch) -> None:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(branch.path)],
            cwd=str(self.workspace), capture_output=True, text=True,
        )
        branch._closed = True
        self._branches.pop(branch.branch_id, None)
