import uuid

from helper.common_functions import get_object
from products.models import Batch


def decrement_batch_quantity(batch_id: uuid, quantity) -> Batch:
    batch = get_object(Batch, id=batch_id)
    batch.quantity -= quantity
    batch.save()
    return batch
