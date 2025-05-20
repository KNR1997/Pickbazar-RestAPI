from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import author_list, author_get_by_slug
from products.services.author_services import author_create, author_update, author_delete
from users.permissions import IsSuperAdminOrStoreOwner


class AuthorListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        image = serializers.JSONField(required=True)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        authors = author_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=authors,
            request=request,
        )


class AuthorDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        bio = serializers.CharField(required=True)
        image = serializers.CharField(required=True)

    def get(self, request, slug):
        author = author_get_by_slug(slug)

        if author is None:
            raise Http404

        data = self.OutputSerializer(author).data

        return Response(data)


class AuthorCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        bio = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        image = serializers.JSONField(required=True, allow_null=True)
        languages = serializers.CharField(required=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = author_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(author).data

        return Response(data)


class AuthorUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, slug):
        serializer = AuthorCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = author_get_by_slug(slug)

        if author is None:
            raise Http404

        author = author_update(author=author, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = AuthorCreateApi.OutputSerializer(author).data

        return Response(data)


class AuthorDeleteApi(APIView):
    @staticmethod
    def delete(request, slug: str):
        author_delete(slug=slug)

        return Response(
            {"detail": "Author successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
