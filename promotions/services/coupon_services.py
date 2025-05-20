from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from promotions.models import Coupon


@transaction.atomic
def coupon_create(*, code: str,
                  description: str,
                  image: str = None,
                  type: str,
                  amount: int,
                  minimum_cart_amount: int,
                  # max_uses: int,
                  active_from: str,
                  expire_at: str,
                  # is_valid: bool,
                  ) -> Coupon:
    coupon = Coupon.objects.create(code=code,
                                   description=description,
                                   image=image,
                                   type=type,
                                   amount=amount,
                                   minimum_cart_amount=minimum_cart_amount,
                                   # max_uses=max_uses,
                                   active_from=active_from,
                                   expire_at=expire_at,
                                   # is_valid=is_valid,
                                   )

    return coupon


@transaction.atomic
def coupon_update(*, coupon: Coupon, data) -> Coupon:
    non_side_effect_fields: List[str] = [
        "code",
        "type",
        "description",
        "amount",
        "minimum_cart_amount",
        "active_from",
        "expire_at",
        "is_approve",
    ]

    coupon, has_updated = model_update(instance=coupon, fields=non_side_effect_fields, data=data)

    # some additional task

    return coupon


@transaction.atomic
def coupon_delete(*, coupon_id: str) -> None:
    coupon = get_object(Coupon, id=coupon_id)
    coupon.delete()
    return None
