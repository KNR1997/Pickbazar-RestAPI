from typing import List

from django.db import transaction
from django.utils.text import slugify

from common.services import model_update
from common.utils import get_object
from promotions.models import FlashSale


def generate_unique_slug(title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1

    while FlashSale.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


@transaction.atomic
def flash_sale_create(*, title: str,
                      description: str = None,
                      start_date: str,
                      end_date: int,
                      type: int,
                      image: str = None,
                      cover_image: str = None,
                      ) -> FlashSale:
    slug = slugify(title)  # Generate slug from title

    flash_sale = FlashSale.objects.create(
        title=title,
        slug=slug,
        description=description,
        start_date=start_date,
        end_date=end_date,
        type=type,
        image=image,
        cover_image=cover_image,
    )

    return flash_sale


@transaction.atomic
def flash_sale_update(*, flash_sale: FlashSale, data) -> FlashSale:
    non_side_effect_fields: List[str] = [
        "title",
        "slug",
        "description",
        "start_date",
        "end_date",
        "type",
        "image",
        "cover_image",
    ]

    flash_sale, has_updated = model_update(instance=flash_sale, fields=non_side_effect_fields, data=data)

    # some additional task

    return flash_sale


@transaction.atomic
def flash_sale_delete(*, flash_sale_id: str) -> None:
    flash_sale = get_object(FlashSale, id=flash_sale_id)
    flash_sale.delete()
    return None
