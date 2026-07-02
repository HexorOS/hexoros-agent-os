# AgentCgroup v0.1 — Tool-Call-Granular Resource Control

Resource control for LLM agents at the granularity that matters:
**the tool call**, not the PID. One agent step can fork 50 subprocesses
(sandbox-exec, browser tab, http fetch) — AgentCgroup binds all of them
to one budget derived from the step's token allowance.

Based on Zheng et al. (2026), *"AgentCgroup: eBPF-based Resource Control
for LLM Agents"*.

## Principles

- **Granularity** — limits per tool call, not per process
- **Adaptivity** — token budget → memory/CPU limits (overridable mapping)
- **Graceful degradation** — throttle → freeze → queue, instead of
  kill-and-restart

## Usage

```python
from agentcgroup import AgentCgroup, Budget

acg = AgentCgroup(agent="hexcoder")

with acg.tool_call("browser-fetch", Budget(tokens=8000)) as tc:
    proc = tc.spawn(["python3", "scrape.py"])
    proc.wait()

print(tc.stats)   # peak_rss, cpu_time, throttle_events, degraded, ...
```

Demo: `python3 examples/agentcgroup_demo.py`

## Backends (auto-detected)

| Backend | Enforcement | Needs |
|---|---|---|
| `cgroup-v2` | in-kernel: `memory.high/max`, `cpu.max`, `pids.max`, `cgroup.freeze` | delegated cgroup subtree (root or systemd delegation) |
| `rlimit-userspace` | POSIX rlimits (hard caps) + /proc monitor with SIGSTOP/SIGCONT duty-cycling (soft throttle) | nothing — runs unprivileged |

Measured (fallback backend, unprivileged sandbox): CPU hog with 40% quota
runs at ~39% effective CPU via duty-cycling; 64 MiB cap stops a runaway
allocator at the limit; well-behaved calls see zero interference.

## Status & roadmap

| Layer | Status |
|---|---|
| Tool-call lifecycle, budget mapping, stats | ✅ v0.1 |
| Userspace fallback backend (rlimit + /proc) | ✅ v0.1, tested |
| cgroup v2 backend (in-kernel enforcement) | ✅ v0.1, needs delegated subtree |
| eBPF in-kernel tool-call-aware policy | 🔭 research track (per the paper; NOT in v0.1) |
| Adaptive re-budgeting mid-call (token burn rate) | 🔜 planned |

v0.1 is dependency-free (stdlib only). The backend interface is stable so
eBPF enforcement can slot in without changing agent code.
