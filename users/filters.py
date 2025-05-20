import django_filters

from users.models import User


class BaseUserFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = ("id", "username", "email")
