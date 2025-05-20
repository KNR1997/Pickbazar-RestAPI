from django.urls import path

from products.apis import type_apis, tag_apis, category_apis, attribute_apis, manufacturer_apis, author_apis, \
    product_apis

urlpatterns = [
    path('types/', type_apis.TypeListApi.as_view()),
    path('types-shop/', type_apis.TypeListShopApi.as_view()),
    path('types/create', type_apis.TypeCreateApi.as_view()),
    path('types/<str:slug>', type_apis.TypeDetailApi.as_view()),
    path('types-shop/<str:slug>', type_apis.TypeDetailApi.as_view()),
    path('types/<int:type_id>/update', type_apis.TypeUpdateApi.as_view()),
    path('types/<int:type_id>/delete', type_apis.TypeDeleteApi.as_view()),

    path('categories/', category_apis.CategoryListApi.as_view()),
    path('categories/create', category_apis.CategoryCreateApi.as_view()),
    path('categories/<slug:slug>', category_apis.CategoryDetailApi.as_view()),
    path('categories/<str:category_id>/update', category_apis.CategoryUpdateApi.as_view()),
    path('categories/<str:category_id>/delete', category_apis.CategoryDeleteApi.as_view()),

    path('tags/', tag_apis.TagListApi.as_view()),
    path('tags/create', tag_apis.TagCreateApi.as_view()),
    path('tags/<str:slug>', tag_apis.TagDetailApi.as_view()),
    path('tags/<str:tag_id>/update', tag_apis.TagUpdateApi.as_view()),
    path('tags/<str:tag_id>/delete', tag_apis.TagDeleteApi.as_view()),

    path('attributes/', attribute_apis.AttributeListApi.as_view()),
    path('attributes/create', attribute_apis.AttributeCreateApi.as_view()),
    path('attributes/<str:slug>', attribute_apis.AttributeDetailApi.as_view()),
    path('attributes/<str:attribute_id>/update', attribute_apis.AttributeUpdateApi.as_view()),
    path('attributes/<str:slug>/delete', attribute_apis.AttributeDeleteApi.as_view()),

    path('manufacturers/', manufacturer_apis.ManufacturerListApi.as_view()),
    path('manufacturers/create', manufacturer_apis.ManufacturerCreateApi.as_view()),
    path('manufacturers/<str:slug>', manufacturer_apis.ManufacturerDetailApi.as_view()),
    path('manufacturers/<str:slug>/update', manufacturer_apis.ManufacturerUpdateApi.as_view()),
    path('manufacturers/<str:slug>/delete', manufacturer_apis.ManufacturerDeleteApi.as_view()),

    path('authors/', author_apis.AuthorListApi.as_view()),
    path('authors/create', author_apis.AuthorCreateApi.as_view()),
    path('authors/<str:slug>', author_apis.AuthorDetailApi.as_view()),
    path('authors/<str:slug>/update', author_apis.AuthorUpdateApi.as_view()),
    path('authors/<str:slug>/delete', author_apis.AuthorDeleteApi.as_view()),

    path('products/', product_apis.ProductListApi.as_view()),
    path('products/create', product_apis.ProductCreateApi.as_view()),
    path('products/<str:slug>', product_apis.ProductDetailApi.as_view()),
    path('products/<str:slug>/update', product_apis.ProductUpdateApi.as_view()),
    path('products/<str:product_id>/delete', product_apis.ProductDeleteApi.as_view()),

]
