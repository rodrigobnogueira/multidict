"""Benchmark: original vs optimized getall() in pure Python MultiDict.

Usage
-----
Run from the project root:

    .venv/bin/python tests/benchmark_getall.py

Results are written to tests/bench_getall_output.txt
"""

import sys
import timeit

from multidict._multidict_py import MultiDict as PyMultiDict


# --- Original implementation (verbatim from master) ---

def _original_getall(md: PyMultiDict, key: str) -> list:
    identity = md._identity(key)
    hash_ = hash(identity)
    res: list = []
    restore: list[int] = []
    for slot, idx, e in md._keys.iter_hash(hash_):
        if e.identity == identity:
            res.append(e.value)
            e.hash = -1
            restore.append(idx)

    if res:
        entries = md._keys.entries
        for idx in restore:
            entries[idx].hash = hash_
        return res
    raise KeyError(key)


# --- Helpers ---

def _create_md(keys: int, values_per_key: int) -> PyMultiDict:
    md: PyMultiDict = PyMultiDict()
    for i in range(keys):
        for j in range(values_per_key):
            md.add(f"key{i}", f"value{i}_{j}")
    return md


# --- Main ---

ITERATIONS = 1000
REPEATS = 5
WARMUP = 2
OUTPUT_FILE = "tests/bench_getall_output.txt"

CONFIGS = [(10, 1), (10, 10), (100, 10), (1000, 10)]


def _run_benchmarks() -> list[str]:
    lines: list[str] = []

    def p(text: str = "") -> None:
        lines.append(text)
        print(text)

    p()
    p("=" * 80)
    p("getall() Benchmark: Original vs Optimized  (Pure Python)")
    p("=" * 80)
    p()
    p(f"Python:      {sys.version}")
    p(f"Method:      min of {REPEATS} trials, each trial = {ITERATIONS} iterations")
    p(f"Warm-up:     {WARMUP} discarded trials before measurement")
    p()
    p("|  Keys | V/Key | Total  | Original (ms) | Optimized (ms) | Speedup |")
    p("|-------|-------|--------|---------------|----------------|---------|")

    for keys, vpk in CONFIGS:
        md = _create_md(keys, vpk)
        keys_list = list(set(md.keys()))

        def run_old() -> None:
            for k in keys_list:
                _original_getall(md, k)

        def run_new() -> None:
            for k in keys_list:
                md.getall(k)

        # Warm-up (discarded)
        timeit.repeat(run_old, number=ITERATIONS, repeat=WARMUP)
        timeit.repeat(run_new, number=ITERATIONS, repeat=WARMUP)

        # Measurement — min of REPEATS trials (most reproducible, per timeit docs)
        t_old = min(timeit.repeat(run_old, number=ITERATIONS, repeat=REPEATS)) * 1000
        t_new = min(timeit.repeat(run_new, number=ITERATIONS, repeat=REPEATS)) * 1000
        speedup = t_old / t_new

        p(
            f"|{keys:>6} |{vpk:>6} |{keys * vpk:>7} "
            f"|{t_old:>14.2f} |{t_new:>15.2f} |{speedup:>8.2f}x |"
        )

    p()
    p("=" * 80)
    p(f"Each value is the min of {REPEATS} trials (most stable, per timeit docs).")
    p("=" * 80)
    p()

    return lines


if __name__ == "__main__":
    result_lines = _run_benchmarks()

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(result_lines))

    print(f"Results written to {OUTPUT_FILE}")
