from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from users.models import Address, User


@transaction.atomic
def address_create(*, user: User,
                   title: str,
                   type: str = None,
                   is_default: bool = None,
                   zip: str = None,
                   city: str = None,
                   state: str = None,
                   country: str = None,
                   street_address: str = None,
                   ) -> Address:
    address = Address.objects.create(user=user,
                                     title=title,
                                     type=type,
                                     is_default=is_default,
                                     zip=zip,
                                     city=city,
                                     state=state,
                                     country=country,
                                     street_address=street_address,
                                     )

    return address


@transaction.atomic
def address_update(*, address: Address, data) -> Address:
    non_side_effect_fields: List[str] = [
        "name",
        "slug",
        "bio",
        "image",
        "cover_image",
        "languages",
        "icon",
    ]

    address, has_updated = model_update(instance=address, fields=non_side_effect_fields, data=data)

    return address


@transaction.atomic
def address_delete(*, slug: str) -> None:
    address = get_object(Address, slug=slug)
    address.delete()
    return None
