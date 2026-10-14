"""Measure warmed cached broker decisions with an independent one-issuance oracle. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 31
# definition: main — line 34
# variable: clock — line 36
# variable: provider — line 37
# variable: broker — line 38
# variable: expected — line 39
# variable: durations — line 40
# variable: _ — line 42
# variable: start — line 43
# variable: _ — line 44
# variable: _ — line 47
# variable: peak — line 47
# variable: report — line 50
# variable: output — line 62
# END CODE MAP

from __future__ import annotations

import json
import platform
import statistics
import time
import tracemalloc
from pathlib import Path

from rotation.broker import Broker
from rotation.simulation import Clock, Scripted

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Run five measured batches after warmup; save ignored informational evidence, not a performance pass/fail budget."""
    clock = Clock()
    provider = Scripted(clock)
    broker = Broker(provider, clock=clock, sleep=clock.sleep)
    expected = broker.get()
    durations = []
    tracemalloc.start()
    for _ in range(5):
        start = time.perf_counter_ns()
        for _ in range(1000):
            assert broker.get() is expected
        durations.append((time.perf_counter_ns() - start) / 1000 / 1e6)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert provider.count == 1 and broker.stats()["requests"] == 5001
    report = {
        "scope": "warmed local cached broker decision; no network/database",
        "platform": platform.system(),
        "python": platform.python_version(),
        "batches": 5,
        "decisions_per_batch": 1000,
        "milliseconds_per_decision": durations,
        "median_ms": statistics.median(durations),
        "peak_python_allocation_bytes": peak,
        "issuances": provider.count,
        "correctness_oracle": "all 5000 cached decisions return the identical initial lease",
    }
    output = ROOT / "out"
    output.mkdir(exist_ok=True)
    (output / "benchmark.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
