import random
from datetime import date
from decimal import Decimal

from synthetic_garment_source.master_data import generate_styles, generate_suppliers
from synthetic_garment_source.orders import generate_orders


def test_orders_obey_business_rules():
    styles = generate_styles(10, random.Random(1))
    suppliers = generate_suppliers(5, random.Random(2))
    orders = list(generate_orders(100, styles, suppliers, date(2025, 1, 1), date(2025, 12, 31), "INR", random.Random(3)))
    assert len(orders) == 100
    assert len({o.order_id for o in orders}) == 100
    for order in orders:
        assert order.style_id in {s.style_id for s in styles}
        assert order.supplier_id in {s.supplier_id for s in suppliers}
        assert order.order_date <= order.receive_date <= order.delivery_date
        assert order.quantity > 0
        assert order.total_amount == (Decimal(order.quantity) * order.unit_price).quantize(Decimal("0.01"))
