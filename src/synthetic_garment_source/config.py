from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    version: str
    seed: int


@dataclass(frozen=True)
class GenerationConfig:
    style_count: int
    supplier_count: int
    record_count: int
    start_date: date
    end_date: date
    output_format: str
    batch_size: int
    currency: str


@dataclass(frozen=True)
class PathsConfig:
    output_dir: Path
    master_dir: Path
    faults_dir: Path
    schema_drift_dir: Path


@dataclass(frozen=True)
class AppConfig:
    dataset: DatasetConfig
    generation: GenerationConfig
    paths: PathsConfig
    config_path: Path


def _require(mapping: dict[str, Any], key: str, section: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing configuration key: {section}.{key}")
    return mapping[key]


def load_config(config_path: str | Path = "config/generation.yaml") -> AppConfig:
    path = Path(config_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Configuration root must be a YAML mapping")

    ds = raw.get("dataset", {})
    gen = raw.get("generation", {})
    paths = raw.get("paths", {})

    dataset = DatasetConfig(
        name=str(_require(ds, "name", "dataset")),
        version=str(_require(ds, "version", "dataset")),
        seed=int(_require(ds, "seed", "dataset")),
    )
    start_date = date.fromisoformat(str(_require(gen, "start_date", "generation")))
    end_date = date.fromisoformat(str(_require(gen, "end_date", "generation")))
    generation = GenerationConfig(
        style_count=int(_require(gen, "style_count", "generation")),
        supplier_count=int(_require(gen, "supplier_count", "generation")),
        record_count=int(_require(gen, "record_count", "generation")),
        start_date=start_date,
        end_date=end_date,
        output_format=str(gen.get("output_format", "all")).lower(),
        batch_size=int(gen.get("batch_size", 5000)),
        currency=str(gen.get("currency", "INR")).upper(),
    )
    base_dir = path.parent.parent
    paths_config = PathsConfig(
        output_dir=(base_dir / str(paths.get("output_dir", "data/generated"))).resolve(),
        master_dir=(base_dir / str(paths.get("master_dir", "data/master"))).resolve(),
        faults_dir=(base_dir / str(paths.get("faults_dir", "data/faults"))).resolve(),
        schema_drift_dir=(base_dir / str(paths.get("schema_drift_dir", "data/schema_drift"))).resolve(),
    )

    if not dataset.name.strip() or not dataset.version.strip():
        raise ValueError("dataset.name and dataset.version cannot be empty")
    for name, value in (
        ("style_count", generation.style_count),
        ("supplier_count", generation.supplier_count),
        ("record_count", generation.record_count),
        ("batch_size", generation.batch_size),
    ):
        if value <= 0:
            raise ValueError(f"generation.{name} must be greater than zero")
    if generation.start_date > generation.end_date:
        raise ValueError("generation.start_date must be on or before end_date")
    if generation.output_format not in {"all", "csv", "jsonl", "parquet"}:
        raise ValueError("generation.output_format must be all, csv, jsonl, or parquet")
    if len(generation.currency) != 3 or not generation.currency.isalpha():
        raise ValueError("generation.currency must be a 3-letter currency code")

    return AppConfig(dataset, generation, paths_config, path)
