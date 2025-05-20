from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object, resolve_foreign_keys
from products.models import Category, Type


@transaction.atomic
def category_create(*, image: str = None,
                    name: str,
                    slug: str,
                    details: str = None,
                    icon: str = None,
                    type_id: str,
                    parent_id: str = None,
                    ) -> Category:
    category = Category.objects.create(image=image,
                                       name=name,
                                       slug=slug,
                                       details=details,
                                       icon=icon,
                                       type_id=type_id,
                                       parent_id=parent_id,
                                       )

    return category


@transaction.atomic
def category_update(*, category: Category, data) -> Category:
    non_side_effect_fields: List[str] = [
        "image",
        "name",
        "slug",
        "display_name",
        "details",
        "icon",
        "hide",
    ]

    # Update the `updated_by` field explicitly
    # category.updated_by = updated_by

    # Handle foreign key fields separately
    foreign_key_fields = {
        "type_id": Type,
        "parent_id": Category,
    }

    # Resolve foreign key fields
    data = resolve_foreign_keys(data, foreign_key_fields)

    all_fields = non_side_effect_fields + ["type", "department", "parent"]
    category, has_updated = model_update(instance=category, fields=all_fields, data=data)

    # Side-effect fields update here (e.g. username is generated based on first & last name)

    # ... some additional tasks with the user ...
    # if "updated_by" not in non_side_effect_fields:
    #     category.save(update_fields=["updated_by"])

    return category


@transaction.atomic
def category_delete(*, category_id: str) -> None:
    sales_advisor = get_object(Category, id=category_id)
    sales_advisor.delete()
    return None
