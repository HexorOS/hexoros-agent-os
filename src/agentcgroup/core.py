"""AgentCgroup v0.1 — tool-call-granular resource control for LLM agents.

Modeled after Zheng et al. (2026), "AgentCgroup: eBPF-based Resource
Control for LLM Agents". Classic cgroups operate on process granularity;
agents operate on *tool-call* granularity — one agent step may fork 50
subprocesses (sandbox-exec, browser tab, http fetch). AgentCgroup maps
resource control onto the tool-call domain:

- **Granularity** — limits per tool call, not per PID
- **Adaptivity**  — limits derived from the step's token budget
- **Graceful degradation** — throttle/freeze/queue instead of kill-and-restart

v0.1 backends (auto-detected):
- ``CgroupV2Backend`` — cgroup v2 (memory.high/max, cpu.max, pids.max,
  cgroup.freeze). In-kernel enforcement, needs a delegated cgroup tree.
  eBPF-based enforcement (tool-call-aware in-kernel policy) is the
  research track and NOT part of v0.1.
- ``RlimitBackend``  — pure-userspace fallback: POSIX rlimits as hard
  caps plus a /proc monitor thread for soft-limit throttling
  (SIGSTOP/SIGCONT duty-cycling). Works unprivileged.
"""

from __future__ import annotations

import os
import resource
import signal
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

__all__ = [
    "AgentCgroup", "Budget", "ToolCall", "ToolCallStats",
    "ToolCallExceeded", "CgroupV2Backend", "RlimitBackend",
    "detect_backend",
]

CGROUP_ROOT = Path("/sys/fs/cgroup")
SLICE = "hexoros.slice"


class ToolCallExceeded(RuntimeError):
    """Hard resource limit breached; tool call was terminated."""


@dataclass(frozen=True)
class Budget:
    """Maps a step's token budget to concrete resource limits.

    The mapping is deliberately simple in v0.1 and fully overridable:
    bigger token budgets buy proportionally more memory and CPU.
    """

    tokens: int = 4096
    memory_max: Optional[int] = None       # bytes, hard cap
    memory_soft: Optional[int] = None      # bytes, throttle threshold
    cpu_quota_pct: Optional[float] = None  # % of one core
    max_procs: int = 32
    wall_timeout_s: Optional[float] = None

    BYTES_PER_TOKEN = 16 * 1024   # 4k tokens -> 64 MiB
    CPU_PCT_PER_KTOKEN = 12.5     # 4k tokens -> 50% of a core

    def resolved(self) -> "Budget":
        mem = self.memory_max or max(32 << 20, self.tokens * self.BYTES_PER_TOKEN)
        soft = self.memory_soft or int(mem * 0.8)
        cpu = self.cpu_quota_pct or min(
            400.0, max(10.0, self.tokens / 1000 * self.CPU_PCT_PER_KTOKEN))
        return Budget(tokens=self.tokens, memory_max=mem, memory_soft=soft,
                      cpu_quota_pct=cpu, max_procs=self.max_procs,
                      wall_timeout_s=self.wall_timeout_s)


@dataclass
class ToolCallStats:
    peak_rss: int = 0
    cpu_time_s: float = 0.0
    wall_time_s: float = 0.0
    throttle_events: int = 0
    frozen_time_s: float = 0.0
    degraded: bool = False        # soft limit was hit at least once
    killed: bool = False          # hard limit terminated the call


# --------------------------------------------------------------------------
# Backends
# --------------------------------------------------------------------------

class CgroupV2Backend:
    """In-kernel enforcement via cgroup v2 (requires delegated subtree).

    Layout: /sys/fs/cgroup/hexoros.slice/<agent>/<toolcall-id>/
    - memory.high = soft limit -> kernel throttles reclaim (graceful)
    - memory.max  = hard limit
    - cpu.max     = quota/period
    - pids.max    = fork bomb guard
    - cgroup.freeze for queue/backpressure
    """

    name = "cgroup-v2"

    def __init__(self, agent: str, call_id: str, budget: Budget):
        self.budget = budget
        self.path = CGROUP_ROOT / SLICE / agent / call_id
        self.path.mkdir(parents=True, exist_ok=True)
        self._write("memory.high", str(budget.memory_soft))
        self._write("memory.max", str(budget.memory_max))
        period = 100_000
        quota = int(period * budget.cpu_quota_pct / 100)
        self._write("cpu.max", f"{quota} {period}")
        self._write("pids.max", str(budget.max_procs))

    @staticmethod
    def available() -> bool:
        # Real cgroup2 mount exposes cgroup.controllers at the root;
        # a plain directory (or no mount) does not.
        if not (CGROUP_ROOT / "cgroup.controllers").is_file():
            return False
        try:
            probe = CGROUP_ROOT / SLICE / f"probe-{os.getpid()}"
            probe.mkdir(parents=True, exist_ok=True)
            probe.rmdir()
            return True
        except OSError:
            return False

    def _write(self, ctl: str, value: str) -> None:
        (self.path / ctl).write_text(value)

    def attach(self, pid: int) -> None:
        self._write("cgroup.procs", str(pid))

    def freeze(self) -> None:
        self._write("cgroup.freeze", "1")

    def thaw(self) -> None:
        self._write("cgroup.freeze", "0")

    def usage(self) -> tuple[int, float]:
        rss = int((self.path / "memory.current").read_text())
        cpu_usec = 0
        for line in (self.path / "cpu.stat").read_text().splitlines():
            if line.startswith("usage_usec"):
                cpu_usec = int(line.split()[1])
        return rss, cpu_usec / 1e6

    def preexec(self):
        return None  # kernel enforces; nothing to do in the child

    def teardown(self) -> None:
        try:
            self.path.rmdir()
        except OSError:
            pass


class RlimitBackend:
    """Unprivileged userspace fallback.

    Hard caps via POSIX rlimits in the child (RLIMIT_AS, RLIMIT_NPROC);
    soft-limit graceful degradation via a monitor thread that samples
    /proc/<pid> and duty-cycles the process group with SIGSTOP/SIGCONT.
    """

    name = "rlimit-userspace"

    def __init__(self, agent: str, call_id: str, budget: Budget):
        self.budget = budget
        self._pgid: Optional[int] = None
        self._frozen = False

    @staticmethod
    def available() -> bool:
        return Path("/proc/self/status").exists()

    def preexec(self):
        b = self.budget

        def _limits():
            os.setsid()  # own process group -> group-wide signals
            resource.setrlimit(resource.RLIMIT_AS, (b.memory_max, b.memory_max))
            try:
                resource.setrlimit(resource.RLIMIT_NPROC,
                                   (b.max_procs, b.max_procs))
            except (ValueError, OSError):
                pass
        return _limits

    def attach(self, pid: int) -> None:
        self._pgid = os.getpgid(pid)

    def freeze(self) -> None:
        if self._pgid and not self._frozen:
            os.killpg(self._pgid, signal.SIGSTOP)
            self._frozen = True

    def thaw(self) -> None:
        if self._pgid and self._frozen:
            os.killpg(self._pgid, signal.SIGCONT)
            self._frozen = False

    def usage(self, pid: Optional[int] = None) -> tuple[int, float]:
        rss, cpu = 0, 0.0
        try:
            status = Path(f"/proc/{pid}/status").read_text()
            for line in status.splitlines():
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1]) * 1024
            stat = Path(f"/proc/{pid}/stat").read_text().split()
            hz = os.sysconf("SC_CLK_TCK")
            cpu = (int(stat[13]) + int(stat[14])) / hz
        except (FileNotFoundError, ProcessLookupError, IndexError):
            pass
        return rss, cpu

    def teardown(self) -> None:
        self.thaw()


def detect_backend():
    return CgroupV2Backend if CgroupV2Backend.available() else RlimitBackend


# --------------------------------------------------------------------------
# Tool-call lifecycle
# --------------------------------------------------------------------------

class ToolCall:
    """One resource-governed tool call. Spawn subprocesses via .spawn();
    every child (and its children) is bound to this call's limits."""

    SAMPLE_INTERVAL = 0.05
    FREEZE_BACKOFF = 0.25   # graceful-degradation pause per throttle event
    MAX_THROTTLES = 8       # after this many soft breaches -> hard stop

    def __init__(self, agent: str, name: str, budget: Budget,
                 backend_cls=None):
        self.agent = agent
        self.name = name
        self.call_id = f"{name}-{uuid.uuid4().hex[:8]}"
        self.budget = budget.resolved()
        backend_cls = backend_cls or detect_backend()
        self.backend = backend_cls(agent, self.call_id, self.budget)
        self.stats = ToolCallStats()
        self._procs: list[subprocess.Popen] = []
        self._stop = threading.Event()
        self._monitor: Optional[threading.Thread] = None
        self._t0 = time.monotonic()

    # -- public ------------------------------------------------------------

    def spawn(self, argv: list[str], **popen_kw) -> subprocess.Popen:
        proc = subprocess.Popen(argv, preexec_fn=self.backend.preexec(),
                                **popen_kw)
        self.backend.attach(proc.pid)
        self._procs.append(proc)
        if self._monitor is None:
            self._monitor = threading.Thread(target=self._watch, daemon=True)
            self._monitor.start()
        return proc

    def close(self) -> None:
        self._stop.set()
        if self._monitor:
            self._monitor.join(timeout=2)
        for p in self._procs:
            if p.poll() is None:
                p.terminate()
        self.stats.wall_time_s = time.monotonic() - self._t0
        self.backend.teardown()

    def __enter__(self) -> "ToolCall":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- monitor: soft-limit graceful degradation ---------------------------

    def _watch(self) -> None:
        while not self._stop.is_set():
            live = [p for p in self._procs if p.poll() is None]
            if not live:
                break
            rss_total, cpu_total = 0, 0.0
            for p in live:
                if isinstance(self.backend, RlimitBackend):
                    rss, cpu = self.backend.usage(p.pid)
                else:
                    rss, cpu = self.backend.usage()
                rss_total += rss
                cpu_total = max(cpu_total, cpu)
            self.stats.peak_rss = max(self.stats.peak_rss, rss_total)
            self.stats.cpu_time_s = max(self.stats.cpu_time_s, cpu_total)

            wall = time.monotonic() - self._t0
            over_mem = rss_total > self.budget.memory_soft
            over_wall = (self.budget.wall_timeout_s is not None
                         and wall > self.budget.wall_timeout_s)
            cpu_pct = (cpu_total / wall * 100) if wall > 0.2 else 0.0
            over_cpu = cpu_pct > self.budget.cpu_quota_pct

            if over_wall or self.stats.throttle_events >= self.MAX_THROTTLES:
                self._hard_stop(live)
                return
            if over_mem or over_cpu:
                # Graceful degradation: freeze -> backoff -> thaw (queue),
                # instead of kill-and-restart.
                self.stats.degraded = True
                self.stats.throttle_events += 1
                self.backend.freeze()
                time.sleep(self.FREEZE_BACKOFF)
                self.stats.frozen_time_s += self.FREEZE_BACKOFF
                self.backend.thaw()
            time.sleep(self.SAMPLE_INTERVAL)

    def _hard_stop(self, procs) -> None:
        self.stats.killed = True
        self.backend.thaw()
        for p in procs:
            if p.poll() is None:
                p.kill()


class AgentCgroup:
    """Per-agent resource-control domain; issues governed tool calls."""

    def __init__(self, agent: str, backend_cls=None):
        self.agent = agent
        self.backend_cls = backend_cls or detect_backend()

    @property
    def backend_name(self) -> str:
        return self.backend_cls.name

    def tool_call(self, name: str, budget: Budget = Budget()) -> ToolCall:
        return ToolCall(self.agent, name, budget, self.backend_cls)
