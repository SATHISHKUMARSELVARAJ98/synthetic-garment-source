from pathlib import Path

import pytest

from synthetic_garment_source.config import load_config


def test_load_default_config():
    config = load_config("config/generation.yaml")
    assert config.dataset.seed == 42
    assert config.generation.style_count == 100
    assert config.generation.supplier_count == 50
    assert config.generation.record_count == 1000
    assert config.generation.output_format == "all"


def test_missing_config_raises():
    with pytest.raises(FileNotFoundError):
        load_config("missing_config.yaml")
