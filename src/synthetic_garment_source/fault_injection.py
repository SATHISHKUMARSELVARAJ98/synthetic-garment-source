from __future__ import annotations

import csv
from pathlib import Path


def inject_fault(source_csv: Path, output_dir: Path, fault: str) -> Path:
    if not source_csv.exists():
        raise FileNotFoundError(f"Generate the clean CSV dataset first: {source_csv}")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"garment_orders_{fault}.csv"
    with source_csv.open(newline="", encoding="utf-8") as src:
        reader = csv.DictReader(src)
        rows = list(reader)
        columns = reader.fieldnames or []
    if not rows:
        raise ValueError("Source orders file has no records")
    row = rows[0]
    if fault == "invalid_quantity":
        row["quantity"] = "0"
    elif fault == "missing_supplier":
        row["supplier_id"] = "SUP99999"
    elif fault == "invalid_date_sequence":
        row["delivery_date"] = "2020-01-01"
    elif fault == "incorrect_total":
        row["total_amount"] = "1.00"
    elif fault == "duplicate_order":
        rows.append(dict(rows[0]))
    else:
        raise ValueError(f"Unsupported fault: {fault}")
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return target
