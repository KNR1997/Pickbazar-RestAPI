from typing import List

from django.db import transaction
from django.utils.text import slugify

from common.services import model_update
from common.utils import get_object
from products.models import Type


@transaction.atomic
def type_create(*, name: str,
                banners: str = None,
                promotional_sliders: str = None,
                icon: str = None,
                settings: str,
                ) -> Type:
    slug = slugify(name)  # Generate slug from title

    _type = Type.objects.create(name=name,
                                slug=slug,
                                banners=banners,
                                promotional_sliders=promotional_sliders,
                                icon=icon,
                                settings=settings,
                                )

    return _type


@transaction.atomic
def type_update(*, _type: Type, data) -> Type:
    non_side_effect_fields: List[str] = [
        "name",
        "icon",
        "settings",
    ]

    _type, has_updated = model_update(instance=_type, fields=non_side_effect_fields, data=data)

    # Side-effect fields update here (e.g. username is generated based on first & last name)

    return _type


@transaction.atomic
def type_delete(*, type_id: str) -> None:
    _type = get_object(Type, id=type_id)
    _type.delete()
    return None
