import random

from synthetic_garment_source.master_data import generate_styles, generate_suppliers


def test_master_data_ids_are_unique():
    styles = generate_styles(30, random.Random(7))
    suppliers = generate_suppliers(20, random.Random(7))
    assert len({s.style_id for s in styles}) == 30
    assert len({s.supplier_id for s in suppliers}) == 20


def test_seed_reproduces_styles():
    first = generate_styles(5, random.Random(42))
    second = generate_styles(5, random.Random(42))
    assert first == second
