from typing import Optional

from django.db.models.query import QuerySet

from common.utils import get_object
from users.filters import BaseUserFilter
from users.models import User, Profile


def user_get_login_data(*, user: User):
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }


def user_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.all()

    return BaseUserFilter(filters, qs).qs


def user_get(user_id) -> Optional[User]:
    user = get_object(User, id=user_id)

    return user


def admin_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.filter(is_admin=True)

    return BaseUserFilter(filters, qs).qs


def profile_get_by_user(base_user: User) -> Optional[Profile]:
    profile = get_object(Profile, user=base_user)

    return profile


def customer_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.filter(groups__name='customer')

    return BaseUserFilter(filters, qs).qs


def vendor_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.filter(groups__name='store_owner')

    return BaseUserFilter(filters, qs).qs
