from typing import List

from django.db import transaction
from django.utils.text import slugify

from common.services import model_update
from common.utils import get_object
from layouts.models import FAQ


@transaction.atomic
def faq_create(*, faq_title: str,
               faq_description: str = None,
               ) -> FAQ:
    slug = slugify(faq_title)  # Generate slug from title

    faq = FAQ.objects.create(faq_title=faq_title,
                             slug=slug,
                             faq_description=faq_description,
                             )

    return faq


@transaction.atomic
def faq_update(*, faq: FAQ, data) -> FAQ:
    non_side_effect_fields: List[str] = [
        "faq_title",
        "faq_description",
    ]

    faq, has_updated = model_update(instance=faq, fields=non_side_effect_fields, data=data)

    return faq


@transaction.atomic
def faq_delete(*, faq_id: str) -> None:
    faq = get_object(FAQ, id=faq_id)
    faq.delete()
    return None
