from __future__ import annotations

import csv
import random
from decimal import Decimal
from pathlib import Path

from .models import Style, Supplier
from .rules import CATEGORIES, CITIES, SEASONS, SUPPLIER_NAMES, money


def generate_styles(count: int, rng: random.Random) -> list[Style]:
    styles = []
    for i in range(1, count + 1):
        category = rng.choice(CATEGORIES)
        styles.append(Style(
            style_id=f"ST{i:05d}",
            style_name=f"{category.replace(' ', '')}-{i:05d}",
            category=category,
            season=rng.choice(SEASONS),
            base_unit_price=money(Decimal(str(rng.uniform(180, 1800)))),
        ))
    return styles


def generate_suppliers(count: int, rng: random.Random) -> list[Supplier]:
    suppliers = []
    for i in range(1, count + 1):
        base = SUPPLIER_NAMES[(i - 1) % len(SUPPLIER_NAMES)]
        suffix = f" {((i - 1) // len(SUPPLIER_NAMES)) + 1}" if i > len(SUPPLIER_NAMES) else ""
        suppliers.append(Supplier(
            supplier_id=f"SUP{i:05d}",
            supplier_name=base + suffix,
            city=rng.choice(CITIES),
            country="India",
        ))
    return suppliers


def write_dataclasses_csv(records: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    fieldnames = list(records[0].__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {key: str(value) if isinstance(value, Decimal) else value for key, value in record.__dict__.items()}
            writer.writerow(row)
