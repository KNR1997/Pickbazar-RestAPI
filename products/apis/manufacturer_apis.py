from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import tag_list, tag_get_by_slug, tag_get, manufacturer_list, manufacturer_get_by_slug
from products.serializers import TypeSerializer
from products.services.manufacturer_services import manufacture_create, manufacture_update
from products.services.tag_services import tag_create, tag_update, tag_delete
from users.permissions import IsSuperAdminOrStoreOwner


class ManufacturerListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        manufacturers = manufacturer_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=manufacturers,
            request=request,
        )


class ManufacturerDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        description = serializers.CharField(required=True)
        image = serializers.CharField(required=True)
        language = serializers.CharField()
        translated_languages = serializers.JSONField()
        type = TypeSerializer(required=False)

    def get(self, request, slug):
        manufacture = manufacturer_get_by_slug(slug)

        if manufacture is None:
            raise Http404

        data = self.OutputSerializer(manufacture).data

        return Response(data)


class ManufacturerCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        website = serializers.CharField(required=True)
        description = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        image = serializers.JSONField(required=True, allow_null=True)
        type_id = serializers.IntegerField(required=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manufacture = manufacture_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(manufacture).data

        return Response(data)


class ManufacturerUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, slug):
        serializer = ManufacturerCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manufacturer = manufacturer_get_by_slug(slug)

        if manufacturer is None:
            raise Http404

        manufacturer = manufacture_update(manufacturer=manufacturer, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = ManufacturerCreateApi.OutputSerializer(manufacturer).data

        return Response(data)


class ManufacturerDeleteApi(APIView):
    @staticmethod
    def delete(request, tag_id: str):
        tag_delete(tag_id=tag_id)

        return Response(
            {"detail": "Tag successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
