from __future__ import annotations

import csv
from pathlib import Path


def create_schema_drift(source_csv: Path, output_dir: Path) -> Path:
    if not source_csv.exists():
        raise FileNotFoundError(f"Generate the clean CSV dataset first: {source_csv}")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "garment_orders_schema_drift.csv"
    with source_csv.open(newline="", encoding="utf-8") as src:
        reader = csv.DictReader(src)
        original_columns = list(reader.fieldnames or [])
        rows = list(reader)
    drift_columns = original_columns + ["factory_code"]
    for i, row in enumerate(rows):
        row["factory_code"] = f"FAC{(i % 12) + 1:03d}"
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=drift_columns)
        writer.writeheader()
        writer.writerows(rows)
    return target
