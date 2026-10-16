# Synthetic Garment ERP Source Generator

A reproducible, configurable synthetic data generator that simulates an upstream garment ERP system. It creates master data and garment-order transactions for practicing data engineering without using confidential company data.

## Features

- YAML configuration with validation.
- Seeded random generation for repeatable datasets.
- Style and supplier master data with unique keys.
- Garment orders with foreign-key integrity and business rules.
- CSV, JSON Lines (`.jsonl`), and Parquet outputs.
- Streaming order generation and batched Parquet writes.
- Data validation, controlled fault injection, schema-drift samples.
- Dataset manifest with row counts, schema, checksums, and generation metadata.
- Benchmark command and pytest suite.

## Requirements

- Python 3.12+
- Windows PowerShell, macOS, or Linux

## 1. Install

From this directory:

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

### macOS/Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 2. Configure

Edit `config/generation.yaml`. The default is 100 styles, 50 suppliers, and 1,000 orders with seed 42. The output format setting accepts `all`, `csv`, `jsonl`, or `parquet`.

## 3. Generate the dataset

```bash
garment-source generate all
```

Or without installing the console command:

```bash
python -m synthetic_garment_source.cli generate all
```

Generated files appear under `data/generated/v1.0.0/`:
- `master/styles.csv`
- `master/suppliers.csv`
- `orders/garment_orders.csv`
- `orders/garment_orders.jsonl`
- `orders/garment_orders.parquet`
- `manifest.json`

Generation is deterministic for a fixed seed and unchanged generator/configuration. Changing code can change output even with the same seed.

## 4. Validate

```bash
garment-source validate
```

A successful run exits with code 0. Validation checks required columns, duplicate IDs, foreign keys, quantities, dates, and amount calculations. A failed validation exits non-zero.

## 5. Other commands

```bash
garment-source generate master
garment-source generate orders
garment-source inject-fault --fault invalid_quantity
garment-source inject-fault --fault missing_supplier
garment-source schema-drift
garment-source benchmark --orders 100000
garment-source --help
```

Fault injection writes a separate deliberately-invalid CSV under `data/faults/`; it does not corrupt the clean dataset. Schema drift writes a separate example under `data/schema_drift/`.

## 6. Tests

```bash
pytest -v
```

## Output schema

| Column | Meaning |
|---|---|
| `order_id` | Unique order ID |
| `style_id` | Foreign key to styles |
| `supplier_id` | Foreign key to suppliers |
| `order_date` | Order creation date |
| `receive_date` | Expected/recorded receipt date |
| `delivery_date` | Delivery date |
| `quantity` | Units ordered; positive integer |
| `unit_price` | Unit price stored as a decimal string |
| `total_amount` | `quantity × unit_price`, decimal string |
| `currency` | Currency code |
| `status` | Order lifecycle status |

## Project structure

```text
synthetic_garment_source/
├── config/generation.yaml
├── data/
│   ├── generated/v1.0.0/
│   ├── faults/
│   └── schema_drift/
├── src/synthetic_garment_source/
│   ├── __init__.py
│   ├── benchmark.py
│   ├── cli.py
│   ├── config.py
│   ├── fault_injection.py
│   ├── generator.py
│   ├── manifest.py
│   ├── master_data.py
│   ├── models.py
│   ├── orders.py
│   ├── rules.py
│   ├── schema_drift.py
│   ├── validation.py
│   └── writer.py
└── tests/
```

## Design notes

- The source generator is intentionally separate from the Part 2 ETL pipeline.
- It only writes synthetic files; it does not connect to or modify an operational ERP database.
- CSV and JSONL are stream-written. Parquet is written in batches.
- The manifest is written last so it describes the completed output files.
- For a large dataset, raise `record_count` in YAML or pass `--orders` to the benchmark command. Ensure enough disk space is available.
