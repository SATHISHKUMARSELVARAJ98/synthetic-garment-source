from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterator, Sequence

from .models import GarmentOrder, Style, Supplier
from .rules import STATUSES, money


def _random_date(rng: random.Random, start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, span))


def generate_orders(
    count: int,
    styles: Sequence[Style],
    suppliers: Sequence[Supplier],
    start_date: date,
    end_date: date,
    currency: str,
    rng: random.Random,
) -> Iterator[GarmentOrder]:
    if not styles or not suppliers:
        raise ValueError("At least one style and one supplier are required")
    for i in range(1, count + 1):
        order_date = _random_date(rng, start_date, end_date)
        receive_date = order_date + timedelta(days=rng.randint(1, 30))
        delivery_date = receive_date + timedelta(days=rng.randint(1, 45))
        style = rng.choice(styles)
        supplier = rng.choice(suppliers)
        quantity = rng.randrange(100, 5001, 100)
        unit_price = money(style.base_unit_price * Decimal(str(rng.uniform(0.85, 1.20))))
        total_amount = money(Decimal(quantity) * unit_price)
        yield GarmentOrder(
            order_id=f"ORD{i:09d}",
            style_id=style.style_id,
            supplier_id=supplier.supplier_id,
            order_date=order_date,
            receive_date=receive_date,
            delivery_date=delivery_date,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency=currency,
            status=rng.choice(STATUSES),
        )
