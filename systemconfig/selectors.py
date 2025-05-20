from typing import Optional

from common.utils import get_object
from systemconfig.models import Settings


def settings_get(settings_id) -> Optional[Settings]:
    settings = get_object(Settings, id=settings_id)

    return settings
