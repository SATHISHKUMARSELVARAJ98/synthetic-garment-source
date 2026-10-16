from __future__ import annotations

import time
from dataclasses import replace

from .config import AppConfig
from .generator import generate


def run_benchmark(config: AppConfig, order_count: int) -> dict:
    if order_count <= 0:
        raise ValueError("order_count must be greater than zero")
    started = time.perf_counter()
    result = generate(config, target="orders", order_count=order_count)
    elapsed = time.perf_counter() - started
    return {
        "orders": order_count,
        "elapsed_seconds": round(elapsed, 3),
        "orders_per_second": round(order_count / elapsed, 2) if elapsed else None,
        "output_dir": str(result["version_root"]),
    }
