from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import attribute_list, attribute_get_by_slug, attribute_get
from products.serializers import AttributeValueSerializer
from products.services.attribute_services import attribute_create, attribute_update, attribute_delete
from users.permissions import IsSuperAdminOrStoreOwner


class AttributeListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        values = AttributeValueSerializer(many=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        attributes = attribute_list(filters=filters_serializer.validated_data)

        first_attribute = attributes.first()

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=attributes,
            request=request,
        )


class AttributeDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        language = serializers.CharField(required=True)
        translated_languages = serializers.CharField(required=True)
        values = AttributeValueSerializer(many=True)

    def get(self, request, slug):
        attribute = attribute_get_by_slug(slug)

        if attribute is None:
            raise Http404

        data = self.OutputSerializer(attribute).data

        return Response(data)


class AttributeCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        # slug = serializers.CharField(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attribute = attribute_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(attribute).data

        return Response(data)


class AttributeUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        values = serializers.ListField(child=serializers.DictField(), default=list)

    @transaction.atomic
    def put(self, request, attribute_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attribute = attribute_get(attribute_id)

        if attribute is None:
            raise Http404

        attribute = attribute_update(attribute=attribute, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = AttributeCreateApi.OutputSerializer(attribute).data

        return Response(data)


class AttributeDeleteApi(APIView):
    @staticmethod
    def delete(request, slug: str):
        attribute_delete(slug=slug)

        return Response(
            {"detail": "Tag successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
