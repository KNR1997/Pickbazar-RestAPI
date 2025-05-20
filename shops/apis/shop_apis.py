from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import tag_list, tag_get_by_slug, tag_get
from products.serializers import TypeSerializer
from products.services.tag_services import tag_create, tag_update, tag_delete
from shops.selectors import shop_list
from users.permissions import IsSuperAdminOrStoreOwner


class ShopListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        slug = serializers.CharField()
        type = TypeSerializer(required=False)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        shops = shop_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=shops,
            request=request,
        )


class ShopDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        details = serializers.CharField(required=True)
        icon = serializers.CharField(required=True)
        # language = serializers.CharField()
        translated_languages = serializers.JSONField()
        type = serializers.SerializerMethodField(required=False)

        @staticmethod
        def get_type(obj):
            return {
                'id': obj.type.id,
                'name': obj.type.name,
                'slug': obj.type.slug,
            } if obj.type else None

    def get(self, request, slug):
        tag = tag_get_by_slug(slug)

        if tag is None:
            raise Http404

        data = self.OutputSerializer(tag).data

        return Response(data)


class ShopCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        details = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        image = serializers.JSONField(required=True, allow_null=True)
        icon = serializers.JSONField(required=True, allow_null=True)
        type_id = serializers.IntegerField(required=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag = tag_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(tag).data

        return Response(data)


class ShopUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, tag_id):
        serializer = ShopCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tag = tag_get(tag_id)

        if tag is None:
            raise Http404

        tag = tag_update(tag=tag, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = ShopCreateApi.OutputSerializer(tag).data

        return Response(data)


class ShopDeleteApi(APIView):
    @staticmethod
    def delete(request, tag_id: str):
        tag_delete(tag_id=tag_id)

        return Response(
            {"detail": "Tag successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
