from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from ecommerce.models import Tax


@transaction.atomic
def tax_create(*, name: str,
               rate: str,
               country: str = None,
               city: str = None,
               state: str = None,
               zip: str = None,
               ) -> Tax:
    tax = Tax.objects.create(name=name,
                             rate=rate,
                             country=country,
                             city=city,
                             state=state,
                             zip=zip,
                             )

    return tax


@transaction.atomic
def tax_update(*, tax: Tax, data) -> Tax:
    non_side_effect_fields: List[str] = [
        "name",
        "rate",
        "country",
        "city",
        "state",
        "zip",
    ]

    tax, has_updated = model_update(instance=tax, fields=non_side_effect_fields, data=data)

    return tax


@transaction.atomic
def tax_delete(*, tax_id: str) -> None:
    tax = get_object(Tax, id=tax_id)
    tax.delete()
    return None
