from datetime import date
from decimal import Decimal, ROUND_HALF_UP

CATEGORIES = ("T-Shirt", "Polo", "Shirt", "Hoodie", "Jogger", "Dress", "Jacket")
SEASONS = ("SS25", "AW25", "SS26", "AW26", "SS27")
CITIES = ("Tiruppur", "Coimbatore", "Chennai", "Bengaluru", "Mumbai", "Ludhiana")
SUPPLIER_NAMES = (
    "Southern Stitch Works", "Cauvery Garments", "Lotus Apparel", "Blue Loom Textiles",
    "Prime Knitwear", "Cotton Route Exports", "Meridian Clothing", "Evergreen Fashions",
)
STATUSES = ("CREATED", "APPROVED", "IN_PRODUCTION", "READY", "SHIPPED", "DELIVERED")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def valid_order_dates(order_date: date, receive_date: date, delivery_date: date) -> bool:
    return order_date <= receive_date <= delivery_date
