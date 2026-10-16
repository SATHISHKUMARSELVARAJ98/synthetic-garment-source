from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Style:
    style_id: str
    style_name: str
    category: str
    season: str
    base_unit_price: Decimal


@dataclass(frozen=True)
class Supplier:
    supplier_id: str
    supplier_name: str
    city: str
    country: str


@dataclass(frozen=True)
class GarmentOrder:
    order_id: str
    style_id: str
    supplier_id: str
    order_date: date
    receive_date: date
    delivery_date: date
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    status: str

    def to_record(self) -> dict[str, str | int]:
        record = asdict(self)
        for field in ("order_date", "receive_date", "delivery_date"):
            record[field] = record[field].isoformat()
        for field in ("unit_price", "total_amount"):
            record[field] = format(record[field], ".2f")
        return record
