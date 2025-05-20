from django.urls import path

from promotions.apis import coupon_apis, flash_sale_apis, review_apis
from shops.apis import shop_apis

urlpatterns = [

    path('coupons/', coupon_apis.CouponListApi.as_view()),
    # path('categories/create', category_apis.CategoryCreateApi.as_view()),
    # path('categories/<slug:slug>', category_apis.CategoryDetailApi.as_view()),
    # path('categories/<str:category_id>/update', category_apis.CategoryUpdateApi.as_view()),
    # path('categories/<str:category_id>/delete', category_apis.CategoryDeleteApi.as_view()),

    path('flash-sale/', flash_sale_apis.FlashSaleListApi.as_view()),
    # path('categories/create', category_apis.CategoryCreateApi.as_view()),
    # path('categories/<slug:slug>', category_apis.CategoryDetailApi.as_view()),
    # path('categories/<str:category_id>/update', category_apis.CategoryUpdateApi.as_view()),
    # path('categories/<str:category_id>/delete', category_apis.CategoryDeleteApi.as_view()),

    path('reviews/', review_apis.ReviewListApi.as_view()),
    # path('categories/create', category_apis.CategoryCreateApi.as_view()),
    # path('categories/<slug:slug>', category_apis.CategoryDetailApi.as_view()),
    # path('categories/<str:category_id>/update', category_apis.CategoryUpdateApi.as_view()),
    # path('categories/<str:category_id>/delete', category_apis.CategoryDeleteApi.as_view()),

]
