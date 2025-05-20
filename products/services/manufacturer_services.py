from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object, resolve_foreign_keys
from products.models import Manufacturer, Type


@transaction.atomic
def manufacture_create(*, name: str,
                       slug: str,
                       description: str = None,
                       image: str = None,
                       cover_image: str = None,
                       website: str = None,
                       type_id: str = None,
                       ) -> Manufacturer:
    manufacture = Manufacturer.objects.create(name=name,
                                              slug=slug,
                                              description=description,
                                              image=image,
                                              cover_image=cover_image,
                                              website=website,
                                              type_id=type_id,
                                              )

    return manufacture


@transaction.atomic
def manufacture_update(*, manufacturer: Manufacturer, data) -> Manufacturer:
    non_side_effect_fields: List[str] = [
        "name",
        "slug",
        "description",
        "website",
        "image",
        "cover_image",
    ]

    # Handle foreign key fields separately
    foreign_key_fields = {
        "type_id": Type,
    }

    # Resolve foreign key fields
    data = resolve_foreign_keys(data, foreign_key_fields)

    all_fields = non_side_effect_fields + ["type"]
    manufacturer, has_updated = model_update(instance=manufacturer, fields=all_fields, data=data)

    return manufacturer


@transaction.atomic
def manufacture_delete(*, slug: str) -> None:
    manufacture = get_object(Manufacturer, slug=slug)
    manufacture.delete()
    return None
