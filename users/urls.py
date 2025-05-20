from django.urls import path

from users.apis import user_apis, admin_apis, customer_apis, vendor_apis

urlpatterns = [
    path("users/", user_apis.UserListApi.as_view(), name="list"),
    path("users/create/", user_apis.UserCreateApi.as_view(), name="create"),
    path("users/<int:user_id>/", user_apis.UserDetailApi.as_view(), name="detail"),
    path("users/<int:user_id>/update/", user_apis.UserUpdateApi.as_view(), name="update"),

    path("customers/list/", customer_apis.CustomerListApi.as_view(), name="list"),

    path("admin/list/", admin_apis.AdminListApi.as_view(), name="list"),

    path("vendors/list/", vendor_apis.VendorListApi.as_view(), name="list"),

    path('me', user_apis.MeApi.as_view()),

]
