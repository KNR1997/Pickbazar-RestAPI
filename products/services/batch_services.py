import uuid
from decimal import Decimal
from typing import Optional

from django.db import transaction

from products.models import Batch, Product, ProductVariation
from products.selectors import batch_get


@transaction.atomic
def batch_create(
        *, product: Product,
        variation: ProductVariation = None,
        batch_number: str,
        quantity: Decimal,
        received_date: str = None,
        manufacture_date: str = None,
        expiry_date: str = None,
        cost: Decimal = None,
        price: Decimal = None,
        sale_price: Decimal = None,
        wholesale_price: Decimal = None,
) -> Batch:
    batch = Batch.objects.create(product=product,
                                 # variation=variation,
                                 batch_number=batch_number,
                                 quantity=quantity,
                                 received_date=received_date,
                                 manufacture_date=manufacture_date,
                                 expiry_date=expiry_date,
                                 cost=cost,
                                 price=price,
                                 sale_price=sale_price,
                                 # wholesale_price=wholesale_price
                                 )

    return batch


@transaction.atomic
def batch_quantity_decrement(*, batch_id: uuid,
                             decrement_value: int) -> Optional[Batch]:
    batch = batch_get(batch_id=batch_id)
    batch.quantity -= decrement_value
    batch.save()
    return batch


@transaction.atomic
def batch_quantity_increment(*, batch_id: str,
                             decrement_value: int) -> Optional[Batch]:
    batch = batch_get(batch_id=batch_id)
    batch.quantity += decrement_value
    batch.save()
    return batch


@transaction.atomic
def batch_update_by_grn(*, batch: Batch, data) -> Batch:
    batch.cost = data.get("cost")
    batch.price = data.get("price")
    batch.quantity = batch.quantity + data.get("quantity")

    batch.clean()
    batch.save()

    return batch
