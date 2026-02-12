"""Benchmark: reversed unique keys via to_dict() vs manual approaches."""

import timeit
import gc
from multidict._multidict import MultiDict as CMultiDict, CIMultiDict as CCIMultiDict
from multidict._multidict_py import MultiDict as PyMultiDict


def create_multidict(cls: type, num_keys: int, vals_per_key: int) -> object:
    items = [(f"key{i % num_keys}", f"value{i}") for i in range(num_keys * vals_per_key)]
    return cls(items)


def timed(func: object, iterations: int = 5000) -> float:
    gc_old = gc.isenabled()
    gc.disable()
    try:
        return timeit.timeit(func, number=iterations)
    finally:
        if gc_old:
            gc.enable()


def bench_to_dict_reversed(md: object) -> list[str]:
    return list(reversed(md.to_dict().keys()))


def bench_manual_reversed(md: object) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for k in md.keys():
        if k not in seen:
            seen.add(k)
            unique.append(k)
    unique.reverse()
    return unique


def run_scenario(label: str, num_keys: int, vals_per_key: int, iters: int) -> None:
    c_md = create_multidict(CMultiDict, num_keys, vals_per_key)

    t_todict = timed(lambda: bench_to_dict_reversed(c_md), iters)
    t_manual = timed(lambda: bench_manual_reversed(c_md), iters)
    ratio = t_manual / t_todict if t_todict > 0 else 0

    print(
        f"| {label:<18} | {num_keys:>5} | {vals_per_key:>5} | "
        f"{t_todict * 1000:>10.2f} | {t_manual * 1000:>10.2f} | "
        f"{ratio:>7.2f}x |"
    )


def run_ci_scenario(num_keys: int, vals_per_key: int, iters: int) -> None:
    items = [(f"Key{i % num_keys}", f"val{i}") for i in range(num_keys * vals_per_key)]
    ci_md = CCIMultiDict(items)

    t_todict = timed(lambda: bench_to_dict_reversed(ci_md), iters)
    t_manual = timed(lambda: bench_manual_reversed(ci_md), iters)
    ratio = t_manual / t_todict if t_todict > 0 else 0

    print(
        f"| {'CIMultiDict':<18} | {num_keys:>5} | {vals_per_key:>5} | "
        f"{t_todict * 1000:>10.2f} | {t_manual * 1000:>10.2f} | "
        f"{ratio:>7.2f}x |"
    )


def main() -> None:
    iters = 5000
    print("\n" + "=" * 85)
    print("Reversed Unique Keys Benchmark: to_dict().keys() vs Manual Approach")
    print("=" * 85)
    print(f"\n{'Iterations per test:':<30} {iters}")
    print(f"{'Time unit:':<30} milliseconds (total for {iters} calls)\n")

    header = (
        f"| {'Approach':<18} | {'Keys':>5} | {'V/Key':>5} | "
        f"{'to_dict ms':>10} | {'manual ms':>10} | {'manual/':>7} |"
    )
    sep = "|" + "-" * 20 + "|" + "-" * 7 + "|" + "-" * 7 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 9 + "|"
    print(header)
    print(sep)

    scenarios = [
        ("MultiDict (small)", 10, 1),
        ("MultiDict (medium)", 50, 5),
        ("MultiDict (large)", 200, 10),
        ("MultiDict (xlarge)", 1000, 10),
    ]
    for label, nk, vpk in scenarios:
        run_scenario(label, nk, vpk, iters)

    run_ci_scenario(50, 5, iters)

    print("\n" + "=" * 85)
    print("Ratio > 1 means to_dict() approach is faster than manual iteration.")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    main()
