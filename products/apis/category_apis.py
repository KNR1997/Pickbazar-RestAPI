from django.db import transaction
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from common.views import BaseAPIView
from products.selectors import category_list, category_get_by_slug, category_get
from products.serializers import TypeSerializer
from products.services.category_services import category_create, category_update, category_delete


class CategoryListApi(BaseAPIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=False)
        name = serializers.CharField()
        details = serializers.CharField()
        icon = serializers.CharField()
        slug = serializers.CharField()
        image = serializers.JSONField()
        type_name = serializers.CharField(source='type.name')

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        categories = category_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=categories,
            request=request,
        )


class CategoryDetailApi(BaseAPIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        slug = serializers.CharField()
        image = serializers.JSONField()
        details = serializers.CharField()
        icon = serializers.CharField()
        language = serializers.CharField()
        translated_languages = serializers.JSONField()
        type = TypeSerializer(required=False)
        # parent = CategorySerializer(required=False)

    def get(self, request, slug):
        category = category_get_by_slug(slug)

        if category is None:
            raise Http404

        data = self.OutputSerializer(category).data

        return Response(data)


class CategoryCreateApi(BaseAPIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()
        slug = serializers.CharField()
        image = serializers.JSONField(required=False)
        details = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        icon = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        type_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
        parent_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @swagger_auto_schema(
        # tags=["Category"],
        operation_description="Endpoint Operation Description",
        request_body=InputSerializer,
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @transaction.atomic
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = category_create(
            **serializer.validated_data,
        )

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = CategoryDetailApi.OutputSerializer(category).data

        return Response(data)


class CategoryUpdateApi(BaseAPIView):

    @transaction.atomic
    def put(self, request, category_id):
        serializer = CategoryCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = category_get(category_id)

        if category is None:
            raise Http404

        category = category_update(category=category, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = CategoryDetailApi.OutputSerializer(category).data

        return Response(data)


class CategoryDeleteApi(BaseAPIView):
    @staticmethod
    def delete(request, category_id: str):
        category_delete(category_id=category_id)

        return Response(
            {"detail": "Category successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )


class ProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    product_type = serializers.CharField()
    description = serializers.CharField()
    image = serializers.JSONField()
    batch_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    batch_sale_price = serializers.DecimalField(max_digits=10, decimal_places=2)
