"""BranchContext — speculative fork-explore-commit execution for HexorOS agents."""

from .core import (
    Branch,
    BranchContext,
    BranchContextError,
    DirtyWorkspaceError,
    StaleBranchError,
)

__version__ = "0.1.0"
__all__ = [
    "Branch",
    "BranchContext",
    "BranchContextError",
    "DirtyWorkspaceError",
    "StaleBranchError",
]
