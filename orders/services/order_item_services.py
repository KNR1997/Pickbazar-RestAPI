import uuid
from decimal import Decimal
from typing import Optional

from django.db import transaction

from orders.models import OrderItem


@transaction.atomic
def order_item_create(*, item_name: str = None,
                      batch_number: str = None,
                      quantity: int,
                      price: Decimal,
                      cost: Optional[Decimal],  # Todo -> allowed null
                      sale_price: Optional[Decimal],  # Todo -> allowed null
                      percentage_discount: Decimal = Decimal(0),
                      percentage_discount_amount: Decimal = Decimal(0),
                      flat_discount_amount: Decimal = Decimal(0),
                      sale_price_discount_amount: Decimal = Decimal(0),
                      item_value: Decimal = Decimal(0),  # Todo -> this may be generated inside the function

                      order_id: uuid,
                      product_id: uuid,
                      ) -> OrderItem:
    try:
        order_item = OrderItem.objects.create(item_name=item_name,
                                              batch_number=batch_number,
                                              quantity=quantity,
                                              price=price,
                                              cost=cost,
                                              sale_price=sale_price,
                                              percentage_discount=percentage_discount,
                                              percentage_discount_amount=percentage_discount_amount,
                                              flat_discount_amount=flat_discount_amount,
                                              sale_price_discount_amount=sale_price_discount_amount,
                                              item_value=item_value,
                                              item_total=item_value * quantity,

                                              order_id=order_id,
                                              product_id=product_id,
                                              )
        return order_item
    except Exception as e:
        raise Exception(f"Failed to create Order Item. Error: {e}")


@transaction.atomic
def order_item_return(*, order_item: OrderItem,
                      return_quantity: int) -> OrderItem:

    order_item.quantity -= return_quantity
    order_item.return_quantity += return_quantity
    order_item.item_total = order_item.item_value * order_item.quantity
    order_item.save()

    return order_item
