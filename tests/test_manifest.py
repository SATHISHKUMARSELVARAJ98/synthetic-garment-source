from pathlib import Path

from synthetic_garment_source.manifest import sha256_file


def test_sha256_is_stable(tmp_path: Path):
    path = tmp_path / "sample.txt"
    path.write_text("garment data", encoding="utf-8")
    first = sha256_file(path)
    assert first == sha256_file(path)
    assert len(first) == 64
