from __future__ import annotations

import random
from pathlib import Path

from .config import AppConfig, load_config
from .manifest import write_manifest
from .master_data import generate_styles, generate_suppliers, write_dataclasses_csv
from .orders import generate_orders
from .validation import validate_dataset
from .writer import write_orders


def _version_root(config: AppConfig) -> Path:
    return config.paths.output_dir / f"v{config.dataset.version}"


def generate(config: AppConfig, target: str = "all", order_count: int | None = None) -> dict:
    rng = random.Random(config.dataset.seed)
    styles = generate_styles(config.generation.style_count, rng)
    suppliers = generate_suppliers(config.generation.supplier_count, rng)

    version_root = _version_root(config)
    master_dir = version_root / "master"
    orders_dir = version_root / "orders"
    if target in {"all", "master"}:
        write_dataclasses_csv(styles, master_dir / "styles.csv")
        write_dataclasses_csv(suppliers, master_dir / "suppliers.csv")
    if target in {"all", "orders"}:
        # Regenerate masters as well when absent, so orders always have matching dimensions.
        if not (master_dir / "styles.csv").exists() or not (master_dir / "suppliers.csv").exists():
            write_dataclasses_csv(styles, master_dir / "styles.csv")
            write_dataclasses_csv(suppliers, master_dir / "suppliers.csv")
        count = order_count if order_count is not None else config.generation.record_count
        orders = generate_orders(
            count, styles, suppliers, config.generation.start_date, config.generation.end_date,
            config.generation.currency, rng,
        )
        output_paths = write_orders(
            orders, orders_dir, config.generation.output_format, config.generation.batch_size
        )
        csv_path = output_paths.get("csv")
        errors = validate_dataset(master_dir, csv_path) if csv_path else []
        if errors:
            raise RuntimeError("Generated dataset failed validation: " + "; ".join(errors[:10]))
        all_files = list(master_dir.glob("*")) + list(orders_dir.glob("*"))
        manifest_path = write_manifest(
            version_root, config.dataset.name, config.dataset.version, config.dataset.seed,
            config.config_path, all_files,
            {"styles": len(styles), "suppliers": len(suppliers), "orders": count},
        )
        return {
            "version_root": version_root,
            "styles": len(styles),
            "suppliers": len(suppliers),
            "orders": count,
            "files": output_paths,
            "manifest": manifest_path,
        }
    return {"version_root": version_root, "styles": len(styles), "suppliers": len(suppliers)}


def validate_generated(config: AppConfig) -> list[str]:
    root = _version_root(config)
    orders_path = root / "orders" / "garment_orders.csv"
    return validate_dataset(root / "master", orders_path)


def get_config(config_path: str | Path = "config/generation.yaml") -> AppConfig:
    return load_config(config_path)
