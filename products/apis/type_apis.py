from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import type_list, type_get_by_slug, type_get
from products.services.type_services import type_create, type_update, type_delete


class TypeListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        icon = serializers.CharField(required=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        types = type_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=types,
            request=request,
        )


class TypeListShopApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        settings = serializers.JSONField(required=True)
        banners = serializers.JSONField(required=True)
        promotional_sliders = serializers.JSONField(required=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        types = type_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return Response(
            data=self.OutputSerializer(types, many=True).data
        )


class TypeDetailApi(APIView):
    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        banners = serializers.JSONField(required=True)
        promotional_sliders = serializers.JSONField(required=True)
        icon = serializers.CharField()
        language = serializers.CharField()
        translated_languages = serializers.JSONField()
        settings = serializers.JSONField()

    def get(self, request, slug):
        type_ = type_get_by_slug(slug)

        if type_ is None:
            raise Http404

        data = self.OutputSerializer(type_).data

        return Response(data)


class TypeCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()
        icon = serializers.CharField(allow_null=True, allow_blank=True)
        settings = serializers.JSONField()

    @transaction.atomic
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _type = type_create(
            **serializer.validated_data,
        )

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = TypeDetailApi.OutputSerializer(_type).data

        return Response(data)


class TypeUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, type_id):
        serializer = TypeCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _type = type_get(type_id)

        if type is None:
            raise Http404

        _type = type_update(_type=_type, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = TypeDetailApi.OutputSerializer(_type).data

        return Response(data)


class TypeDeleteApi(APIView):
    @staticmethod
    def delete(request, type_id: str):
        type_delete(type_id=type_id)

        return Response(
            {"detail": "Type successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
