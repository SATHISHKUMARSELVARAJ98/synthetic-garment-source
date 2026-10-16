import csv
import random
from datetime import date
from pathlib import Path

from synthetic_garment_source.fault_injection import inject_fault
from synthetic_garment_source.master_data import generate_styles, generate_suppliers, write_dataclasses_csv
from synthetic_garment_source.orders import generate_orders
from synthetic_garment_source.writer import write_orders


def test_fault_injection_does_not_modify_source(tmp_path: Path):
    styles = generate_styles(2, random.Random(1))
    suppliers = generate_suppliers(2, random.Random(2))
    master = tmp_path / "master"
    write_dataclasses_csv(styles, master / "styles.csv")
    write_dataclasses_csv(suppliers, master / "suppliers.csv")
    source = write_orders(
        generate_orders(5, styles, suppliers, date(2025, 1, 1), date(2025, 1, 5), "INR", random.Random(3)),
        tmp_path / "orders", "csv"
    )["csv"]
    before = source.read_bytes()
    faulty = inject_fault(source, tmp_path / "faults", "invalid_quantity")
    assert source.read_bytes() == before
    with faulty.open(newline="", encoding="utf-8") as handle:
        first = next(csv.DictReader(handle))
    assert first["quantity"] == "0"
