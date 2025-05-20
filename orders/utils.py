import decimal
import uuid
from dataclasses import dataclass
from typing import List

from products.selectors import product_get


@dataclass
class OrderItem:
    product_id: uuid
    order_quantity: int


def calculate_order_amount(order_items: List[OrderItem]) -> decimal:
    total_amount = 0.0

    for item in order_items:
        # Fetch product by ID
        product = product_get(item.product_id)
        if product:
            total_amount += product.price * item.order_quantity

    return total_amount
