from rest_framework.permissions import BasePermission


class IsSuperAdminPermission(BasePermission):
    """
    Allows access only to users in the 'super_admin' group.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="super_admin").exists()


class IsSuperAdminOrStoreOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=["super_admin", "store_owner"]).exists()


class IsStaffPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="staff").exists()
