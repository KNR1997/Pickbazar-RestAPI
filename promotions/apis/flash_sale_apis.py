from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import tag_list, tag_get_by_slug, tag_get
from products.serializers import TypeSerializer
from products.services.tag_services import tag_create, tag_update, tag_delete
from promotions.selectors import flash_sale_list, flash_sale_get_by_slug
from promotions.services.flash_sale_services import flash_sale_create, flash_sale_update, flash_sale_delete
from shops.selectors import shop_list
from users.permissions import IsSuperAdminOrStoreOwner


class FlashSaleListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        title = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        title = serializers.CharField()
        slug = serializers.CharField()
        description = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        flash_sales = flash_sale_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=flash_sales,
            request=request,
        )


class FlashSaleDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        title = serializers.CharField()
        slug = serializers.CharField()
        description = serializers.CharField()
        start_date = serializers.CharField()
        end_date = serializers.CharField()
        type = serializers.CharField()
        image = serializers.JSONField()
        cover_image = serializers.JSONField()

    def get(self, request, slug):
        flash_sale = flash_sale_get_by_slug(slug)

        if flash_sale is None:
            raise Http404

        data = self.OutputSerializer(flash_sale).data

        return Response(data)


class FlashSaleCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=True)
        start_date = serializers.CharField(required=True)
        end_date = serializers.CharField(required=True)
        type = serializers.CharField(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flash_sale = flash_sale_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(flash_sale).data

        return Response(data)


class FlashSaleUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, slug):
        serializer = FlashSaleCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flash_sale = flash_sale_get_by_slug(slug)

        if flash_sale is None:
            raise Http404

        flash_sale = flash_sale_update(flash_sale=flash_sale, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = FlashSaleCreateApi.OutputSerializer(flash_sale).data

        return Response(data)


class FlashSaleDeleteApi(APIView):
    @staticmethod
    def delete(request, tag_id: str):
        flash_sale_delete(tag_id=tag_id)

        return Response(
            {"detail": "Tag successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
