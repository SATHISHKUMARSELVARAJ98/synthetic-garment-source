from __future__ import annotations

import csv
import json
from itertools import islice
from pathlib import Path
from typing import Iterable, Iterator

import pyarrow as pa
import pyarrow.parquet as pq

from .models import GarmentOrder

ORDER_COLUMNS = [
    "order_id", "style_id", "supplier_id", "order_date", "receive_date",
    "delivery_date", "quantity", "unit_price", "total_amount", "currency", "status",
]


def _record(order: GarmentOrder) -> dict:
    return order.to_record()


def write_orders(
    orders: Iterable[GarmentOrder],
    output_dir: Path,
    output_format: str = "all",
    batch_size: int = 5000,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    formats = {"csv", "jsonl", "parquet"} if output_format == "all" else {output_format}
    paths = {fmt: output_dir / f"garment_orders.{fmt if fmt != 'jsonl' else 'jsonl'}" for fmt in formats}
    iterator = iter(orders)
    handles = {}
    writers = {}
    parquet_writer = None
    parquet_schema = pa.schema([
        ("order_id", pa.string()), ("style_id", pa.string()), ("supplier_id", pa.string()),
        ("order_date", pa.string()), ("receive_date", pa.string()), ("delivery_date", pa.string()),
        ("quantity", pa.int64()), ("unit_price", pa.decimal128(12, 2)),
        ("total_amount", pa.decimal128(18, 2)), ("currency", pa.string()), ("status", pa.string()),
    ])
    try:
        if "csv" in formats:
            handles["csv"] = paths["csv"].open("w", newline="", encoding="utf-8")
            writers["csv"] = csv.DictWriter(handles["csv"], fieldnames=ORDER_COLUMNS)
            writers["csv"].writeheader()
        if "jsonl" in formats:
            handles["jsonl"] = paths["jsonl"].open("w", encoding="utf-8")
        if "parquet" in formats:
            parquet_writer = pq.ParquetWriter(paths["parquet"], parquet_schema, compression="snappy")

        while True:
            batch = list(islice(iterator, batch_size))
            if not batch:
                break
            records = [_record(order) for order in batch]
            if "csv" in formats:
                writers["csv"].writerows(records)
            if "jsonl" in formats:
                for record in records:
                    handles["jsonl"].write(json.dumps(record, separators=(",", ":")) + "\n")
            if "parquet" in formats:
                parquet_records = []
                for record in records:
                    item = dict(record)
                    item["unit_price"] = __import__("decimal").Decimal(item["unit_price"])
                    item["total_amount"] = __import__("decimal").Decimal(item["total_amount"])
                    parquet_records.append(item)
                table = pa.Table.from_pylist(parquet_records, schema=parquet_schema)
                parquet_writer.write_table(table)
    finally:
        for handle in handles.values():
            handle.close()
        if parquet_writer is not None:
            parquet_writer.close()
    return paths
