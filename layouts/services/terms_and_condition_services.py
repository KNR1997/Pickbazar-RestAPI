from typing import List

from django.db import transaction
from django.utils.text import slugify

from common.services import model_update
from common.utils import get_object
from layouts.models import TermsAndConditions


@transaction.atomic
def terms_and_condition_create(*, title: str,
                               description: str = None,
                               type: str = None,
                               ) -> TermsAndConditions:
    slug = slugify(title)  # Generate slug from title

    terms_and_condition = TermsAndConditions.objects.create(title=title,
                                                            slug=slug,
                                                            description=description,
                                                            type=type,
                                                            )

    return terms_and_condition


@transaction.atomic
def terms_and_condition_update(*, terms_and_condition: TermsAndConditions, data) -> TermsAndConditions:
    non_side_effect_fields: List[str] = [
        "title",
        "slug",
        "description",
        "type",
    ]

    terms_and_condition, has_updated = model_update(instance=terms_and_condition, fields=non_side_effect_fields,
                                                    data=data)

    # some additional task

    return terms_and_condition


@transaction.atomic
def terms_and_condition_delete(*, terms_and_condition_id: str) -> None:
    terms_and_condition = get_object(TermsAndConditions, id=terms_and_condition_id)
    terms_and_condition.delete()
    return None
