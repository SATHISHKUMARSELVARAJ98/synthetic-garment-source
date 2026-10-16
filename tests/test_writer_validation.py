import csv
import random
from datetime import date
from pathlib import Path

from synthetic_garment_source.master_data import generate_styles, generate_suppliers, write_dataclasses_csv
from synthetic_garment_source.orders import generate_orders
from synthetic_garment_source.validation import validate_dataset
from synthetic_garment_source.writer import write_orders


def test_write_and_validate_dataset(tmp_path: Path):
    styles = generate_styles(4, random.Random(10))
    suppliers = generate_suppliers(3, random.Random(11))
    master = tmp_path / "master"
    orders_dir = tmp_path / "orders"
    write_dataclasses_csv(styles, master / "styles.csv")
    write_dataclasses_csv(suppliers, master / "suppliers.csv")
    orders = generate_orders(25, styles, suppliers, date(2025, 1, 1), date(2025, 2, 1), "INR", random.Random(12))
    paths = write_orders(orders, orders_dir, "all", 7)
    assert set(paths) == {"csv", "jsonl", "parquet"}
    assert len(list(csv.DictReader(paths["csv"].open(encoding="utf-8")))) == 25
    assert validate_dataset(master, paths["csv"]) == []
    assert paths["parquet"].stat().st_size > 0
    assert len(paths["jsonl"].read_text(encoding="utf-8").splitlines()) == 25
