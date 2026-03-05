"""Benchmark comparing C vs Python implementation of to_dict()."""

import timeit
import gc
from multidict._multidict import MultiDict as CMultiDict
from multidict._multidict_py import MultiDict as PyMultiDict


def create_multidict(cls, num_keys: int, vals_per_key: int):
    items = [(f"key{i % num_keys}", f"value{i}") for i in range(num_keys * vals_per_key)]
    return cls(items)


def benchmark_to_dict(md, iterations: int = 1000) -> float:
    # Disable GC during timing to reduce noise
    gc_old = gc.isenabled()
    gc.disable()
    try:
        def run():
            md.to_dict()
        return timeit.timeit(run, number=iterations)
    finally:
        if gc_old:
            gc.enable()


def run_benchmark(num_keys: int, vals_per_key: int, iterations: int = 1000) -> None:
    total_items = num_keys * vals_per_key
    c_md = create_multidict(CMultiDict, num_keys, vals_per_key)
    py_md = create_multidict(PyMultiDict, num_keys, vals_per_key)
    
    c_time = benchmark_to_dict(c_md, iterations)
    py_time = benchmark_to_dict(py_md, iterations)
    
    speedup = py_time / c_time if c_time > 0 else 0
    
    print(f"| {num_keys:>6} | {vals_per_key:>6} | {total_items:>7} | {c_time*1000:>10.2f} | {py_time*1000:>10.2f} | {speedup:>7.2f}x |")


def main() -> None:
    print("\n" + "=" * 80)
    print("to_dict() Benchmark: C Extension vs Pure Python")
    print("=" * 80)
    print(f"\n{'Iterations per test:':30} 1000")
    print(f"{'Time unit:':30} milliseconds (total for 1000 calls)\n")
    
    print("|  Keys  | V/Key  |  Total  |   C (ms)   |   Py (ms)  | Speedup |")
    print("|--------|--------|---------|------------|------------|---------|")
    
    scenarios = [
        (10, 1),
        (10, 10),
        (100, 10),
        (1000, 10),
    ]
    
    for num_keys, vals_per_key in scenarios:
        run_benchmark(num_keys, vals_per_key)
    
    print("\n" + "=" * 80)
    print("Speedup = Python time / C time (higher is better for C)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()