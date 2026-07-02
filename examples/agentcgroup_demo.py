#!/usr/bin/env python3
"""AgentCgroup v0.1 demo — tool-call-granular resource control.

Three governed tool calls:
1. CPU hog with a 40% quota  -> duty-cycle throttled, finishes degraded
2. Memory hog vs. 64 MiB cap -> hard rlimit stops runaway allocation
3. Well-behaved call         -> runs clean, no throttle events

Run:  python3 examples/agentcgroup_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agentcgroup import AgentCgroup, Budget  # noqa: E402

PY = sys.executable

CPU_HOG = "import time; t=time.time()\nwhile time.time()-t < 2.5: pass"
MEM_HOG = ("blocks=[]\n"
           "try:\n"
           "    for i in range(10000): blocks.append(bytearray(1<<20))\n"
           "except MemoryError:\n"
           "    print('  [child] MemoryError at %d MiB -> rlimit cap works' % len(blocks))")
POLITE = "import time; time.sleep(0.5); print('  [child] done, no drama')"


def show(label, tc, proc):
    rc = proc.wait()
    tc.close()
    s = tc.stats
    print(f"{label:<22} backend={tc.backend.name:<18} rc={rc}")
    print(f"{'':<22} peak_rss={s.peak_rss/(1<<20):6.1f} MiB  "
          f"cpu={s.cpu_time_s:4.2f}s  wall={s.wall_time_s:4.2f}s")
    print(f"{'':<22} throttles={s.throttle_events}  "
          f"frozen={s.frozen_time_s:.2f}s  degraded={s.degraded}  "
          f"killed={s.killed}\n")
    return s


def main():
    acg = AgentCgroup(agent="hexcoder")
    print(f"agent domain: hexcoder | detected backend: {acg.backend_name}\n")

    # 1) CPU hog, 40% quota -> graceful duty-cycle throttling
    tc = acg.tool_call("cpu-hog", Budget(cpu_quota_pct=40, memory_max=256 << 20))
    p = tc.spawn([PY, "-c", CPU_HOG])
    s1 = show("1. cpu-hog @40%", tc, p)
    assert s1.degraded and s1.throttle_events > 0, "expected CPU throttling"
    eff = s1.cpu_time_s / s1.wall_time_s * 100
    print(f"   -> effective CPU: {eff:.0f}% (quota 40%, unthrottled would be ~100%)\n")

    # 2) Memory hog vs 64 MiB hard cap
    tc = acg.tool_call("mem-hog", Budget(memory_max=64 << 20, cpu_quota_pct=100))
    p = tc.spawn([PY, "-c", MEM_HOG])
    s2 = show("2. mem-hog @64MiB", tc, p)
    assert s2.peak_rss < 96 << 20, "expected memory to stay near the cap"

    # 3) Polite tool call -> zero interference
    tc = acg.tool_call("polite", Budget(tokens=8000))
    p = tc.spawn([PY, "-c", POLITE])
    s3 = show("3. polite call", tc, p)
    assert not s3.degraded and not s3.killed

    print("OK — per-tool-call limits enforced, degradation graceful, "
          "no kill-and-restart.")


if __name__ == "__main__":
    main()
