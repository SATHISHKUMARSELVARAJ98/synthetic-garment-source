from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import run_benchmark
from .config import load_config
from .fault_injection import inject_fault
from .generator import generate, validate_generated
from .schema_drift import create_schema_drift


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthetic Garment ERP Source Data Generator")
    parser.add_argument("--config", default="config/generation.yaml", help="Path to YAML configuration")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate master data and/or orders")
    gen.add_argument("target", choices=("master", "orders", "all"), nargs="?", default="all")
    gen.add_argument("--orders", type=int, help="Override configured transaction count")

    sub.add_parser("validate", help="Validate generated CSV data")

    fault = sub.add_parser("inject-fault", help="Write a separate intentionally-invalid dataset")
    fault.add_argument("--fault", required=True, choices=(
        "invalid_quantity", "missing_supplier", "invalid_date_sequence",
        "incorrect_total", "duplicate_order",
    ))

    sub.add_parser("schema-drift", help="Create an example file with an extra column")

    bench = sub.add_parser("benchmark", help="Generate a dataset and report throughput")
    bench.add_argument("--orders", type=int, default=100000)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        root = config.paths.output_dir / f"v{config.dataset.version}"
        orders_csv = root / "orders" / "garment_orders.csv"

        if args.command == "generate":
            result = generate(config, args.target, args.orders)
            printable = {key: str(value) if isinstance(value, Path) else value for key, value in result.items()}
            if "files" in printable:
                printable["files"] = {key: str(value) for key, value in result["files"].items()}
            print(json.dumps(printable, indent=2))
        elif args.command == "validate":
            errors = validate_generated(config)
            if errors:
                print("VALIDATION FAILED")
                for error in errors[:100]:
                    print(f"- {error}")
                print(f"Total errors: {len(errors)}")
                return 1
            print("VALIDATION PASSED")
        elif args.command == "inject-fault":
            path = inject_fault(orders_csv, config.paths.faults_dir, args.fault)
            print(f"Fault dataset written: {path}")
        elif args.command == "schema-drift":
            path = create_schema_drift(orders_csv, config.paths.schema_drift_dir)
            print(f"Schema-drift dataset written: {path}")
        elif args.command == "benchmark":
            result = run_benchmark(config, args.orders)
            print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
