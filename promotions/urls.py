from django.urls import path

from promotions.apis import coupon_apis, flash_sale_apis

urlpatterns = [

    path('coupons/', coupon_apis.CouponListApi.as_view()),
    path('coupons/create', coupon_apis.CouponCreateApi.as_view()),
    path('coupons/<str:code>', coupon_apis.CouponDetailApi.as_view()),
    path('coupons/<str:coupon_id>/update', coupon_apis.CouponUpdateApi.as_view()),
    path('coupons/<str:coupon_id>/delete', coupon_apis.CouponDeleteApi.as_view()),

    path('flash-sale/', flash_sale_apis.FlashSaleListApi.as_view()),
    path('flash-sale/create', flash_sale_apis.FlashSaleCreateApi.as_view()),
    path('flash-sale/<slug:slug>', flash_sale_apis.FlashSaleDetailApi.as_view()),
    path('flash-sale/<slug:slug>/update', flash_sale_apis.FlashSaleUpdateApi.as_view()),
    path('flash-sale/<str:category_id>/delete', flash_sale_apis.FlashSaleDeleteApi.as_view()),
]
