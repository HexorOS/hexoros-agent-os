"""AgentCgroup — tool-call-granular resource control for HexorOS agents."""

from .core import (
    AgentCgroup,
    Budget,
    CgroupV2Backend,
    RlimitBackend,
    ToolCall,
    ToolCallExceeded,
    ToolCallStats,
    detect_backend,
)

__version__ = "0.1.0"
__all__ = [
    "AgentCgroup", "Budget", "CgroupV2Backend", "RlimitBackend",
    "ToolCall", "ToolCallExceeded", "ToolCallStats", "detect_backend",
]
