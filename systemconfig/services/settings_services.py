from typing import List

from django.db import transaction

from common.services import model_update
from systemconfig.models import Settings


@transaction.atomic
def settings_update(*, settings: Settings, data) -> Settings:
    non_side_effect_fields: List[str] = [
        "options",
    ]

    settings, has_updated = model_update(instance=settings, fields=non_side_effect_fields, data=data)

    return settings
