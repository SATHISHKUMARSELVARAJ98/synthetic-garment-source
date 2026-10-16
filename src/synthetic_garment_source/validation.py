from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


def validate_dataset(master_dir: Path, orders_path: Path) -> list[str]:
    errors: list[str] = []
    styles_path = master_dir / "styles.csv"
    suppliers_path = master_dir / "suppliers.csv"
    if not styles_path.exists():
        return [f"Missing styles file: {styles_path}"]
    if not suppliers_path.exists():
        return [f"Missing suppliers file: {suppliers_path}"]
    if not orders_path.exists():
        return [f"Missing orders file: {orders_path}"]

    with styles_path.open(newline="", encoding="utf-8") as f:
        style_rows = list(csv.DictReader(f))
    with suppliers_path.open(newline="", encoding="utf-8") as f:
        supplier_rows = list(csv.DictReader(f))
    style_ids = [r["style_id"] for r in style_rows]
    supplier_ids = [r["supplier_id"] for r in supplier_rows]
    if len(style_ids) != len(set(style_ids)):
        errors.append("Duplicate style_id values found")
    if len(supplier_ids) != len(set(supplier_ids)):
        errors.append("Duplicate supplier_id values found")
    known_styles, known_suppliers = set(style_ids), set(supplier_ids)

    seen_orders: set[str] = set()
    with orders_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
            "order_id", "style_id", "supplier_id", "order_date", "receive_date",
            "delivery_date", "quantity", "unit_price", "total_amount", "currency", "status",
        }
        if not required.issubset(set(reader.fieldnames or [])):
            return errors + [f"Orders file missing columns: {sorted(required - set(reader.fieldnames or []))}"]
        for line_no, row in enumerate(reader, start=2):
            order_id = row["order_id"]
            if order_id in seen_orders:
                errors.append(f"Line {line_no}: duplicate order_id {order_id}")
            seen_orders.add(order_id)
            if row["style_id"] not in known_styles:
                errors.append(f"Line {line_no}: unknown style_id {row['style_id']}")
            if row["supplier_id"] not in known_suppliers:
                errors.append(f"Line {line_no}: unknown supplier_id {row['supplier_id']}")
            try:
                quantity = int(row["quantity"])
                unit_price = Decimal(row["unit_price"])
                total_amount = Decimal(row["total_amount"])
                if quantity <= 0:
                    errors.append(f"Line {line_no}: quantity must be positive")
                if unit_price <= 0:
                    errors.append(f"Line {line_no}: unit_price must be positive")
                if total_amount != (Decimal(quantity) * unit_price).quantize(Decimal("0.01")):
                    errors.append(f"Line {line_no}: total_amount does not equal quantity * unit_price")
            except (ValueError, InvalidOperation):
                errors.append(f"Line {line_no}: invalid numeric value")
            try:
                from datetime import date
                order_date = date.fromisoformat(row["order_date"])
                receive_date = date.fromisoformat(row["receive_date"])
                delivery_date = date.fromisoformat(row["delivery_date"])
                if not order_date <= receive_date <= delivery_date:
                    errors.append(f"Line {line_no}: order/receive/delivery date sequence is invalid")
            except ValueError:
                errors.append(f"Line {line_no}: invalid date")
    return errors
