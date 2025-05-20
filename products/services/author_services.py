from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from products.models import Author


@transaction.atomic
def author_create(*, name: str,
                  slug: str,
                  bio: str = None,
                  image: str = None,
                  cover_image: str = None,
                  languages: str = None,
                  ) -> Author:
    author = Author.objects.create(name=name,
                                   slug=slug,
                                   bio=bio,
                                   image=image,
                                   cover_image=cover_image,
                                   languages=languages,
                                   )

    return author


@transaction.atomic
def author_update(*, author: Author, data) -> Author:
    non_side_effect_fields: List[str] = [
        "name",
        "slug",
        "bio",
        "image",
        "cover_image",
        "languages",
        "icon",
    ]

    author, has_updated = model_update(instance=author, fields=non_side_effect_fields, data=data)

    return author


@transaction.atomic
def author_delete(*, slug: str) -> None:
    author = get_object(Author, slug=slug)
    author.delete()
    return None
