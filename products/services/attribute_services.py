from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from products.models import Attribute, AttributeValue
from products.selectors import attribute_value_get


@transaction.atomic
def attribute_create(*, name: str,
                     slug: str,
                     ) -> Attribute:
    attribute = Attribute.objects.create(name=name,
                                         slug=slug,
                                         )

    return attribute


@transaction.atomic
def attribute_update(*, attribute: Attribute, data) -> Attribute:
    non_side_effect_fields: List[str] = [
        "name",
        "slug",
    ]

    attribute, has_updated = model_update(instance=attribute, fields=non_side_effect_fields, data=data)

    # Create or Update AttributeValues
    attribute_values = data.get('values', [])
    for attribute_value in attribute_values:
        attr_value_id = attribute_value.get("id")

        if attr_value_id:
            attribute_value_instance = attribute_value_get(attribute_value_id=attr_value_id)
            attribute_value_update(attribute_value=attribute_value_instance, data=attribute_value)
        else:
            attribute_value_create(attribute=attribute,
                                   value=attribute_value.get('value'),
                                   meta=attribute_value.get('meta'),
                                   )

    return attribute


@transaction.atomic
def attribute_delete(*, slug: str) -> None:
    attribute = get_object(Attribute, slug=slug)
    attribute.delete()
    return None


@transaction.atomic
def attribute_value_create(*, attribute: Attribute,
                           value: str,
                           meta: str,
                           ) -> Attribute:
    attribute_value = AttributeValue.objects.create(attribute=attribute,
                                                    value=value,
                                                    meta=meta,
                                                    )

    return attribute_value


@transaction.atomic
def attribute_value_update(*, attribute_value: AttributeValue, data) -> AttributeValue:
    non_side_effect_fields: List[str] = [
        "value",
        "meta",
    ]

    attribute_value, has_updated = model_update(instance=attribute_value, fields=non_side_effect_fields, data=data)

    return attribute_value
