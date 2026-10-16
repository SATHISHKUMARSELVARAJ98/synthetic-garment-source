from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(
    output_root: Path,
    dataset_name: str,
    version: str,
    seed: int,
    config_path: Path,
    files: list[Path],
    row_counts: dict[str, int],
) -> Path:
    manifest = {
        "dataset_name": dataset_name,
        "dataset_version": version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "config_file": config_path.name,
        "row_counts": row_counts,
        "files": [
            {
                "path": str(path.relative_to(output_root)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(files) if path.exists()
        ],
    }
    target = output_root / "manifest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return target
