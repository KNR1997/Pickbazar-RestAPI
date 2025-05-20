from django.urls import path

from ecommerce.apis import tax_apis, shipping_apis

urlpatterns = [
    path('taxes/', tax_apis.TaxListApi.as_view()),
    path('taxes/create', tax_apis.TaxCreateApi.as_view()),
    path('taxes/<int:tax_id>', tax_apis.TaxDetailApi.as_view()),
    path('taxes/<str:tax_id>/update', tax_apis.TaxUpdateApi.as_view()),
    path('taxes/<str:tax_id>/delete', tax_apis.TaxDeleteApi.as_view()),

    path('shippings/', shipping_apis.ShippingListApi.as_view()),
    path('shippings/create', shipping_apis.ShippingCreateApi.as_view()),
    path('shippings/<str:shipping_id>', shipping_apis.ShippingDetailApi.as_view()),
    path('shippings/<str:shipping_id>/update', shipping_apis.ShippingUpdateApi.as_view()),
    path('shippings/<str:shipping_id>/delete', shipping_apis.ShippingDeleteApi.as_view()),
]
