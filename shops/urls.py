from django.urls import path

from shops.apis import shop_apis

urlpatterns = [

    path('shops/', shop_apis.ShopListApi.as_view()),
    # path('categories/create', category_apis.CategoryCreateApi.as_view()),
    # path('categories/<slug:slug>', category_apis.CategoryDetailApi.as_view()),
    # path('categories/<str:category_id>/update', category_apis.CategoryUpdateApi.as_view()),
    # path('categories/<str:category_id>/delete', category_apis.CategoryDeleteApi.as_view()),
]
