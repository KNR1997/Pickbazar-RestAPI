from django.urls import path

from orders.apis import order_apis

urlpatterns = [
    path('orders/', order_apis.OrderListApi.as_view()),
    path('orders/create', order_apis.OrderCreateApi.as_view()),
    path('shop/orders/create', order_apis.ShopOrderCreateApi.as_view()),
    path('orders/<str:order_id>', order_apis.OrderDetailApi.as_view()),
    path('orders/<str:order_id>/update', order_apis.OrderUpdateApi.as_view()),
    path('orders/<str:tag_id>/delete', order_apis.OrderDeleteApi.as_view()),
    path('orders/checkout/verify', order_apis.OrderCheckoutVerifyApi.as_view()),

]
