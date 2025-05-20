from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from layouts.selectors import terms_and_conditions_list, terms_and_conditions_get_by_slug, terms_and_conditions_get
from layouts.services.terms_and_condition_services import terms_and_condition_create, terms_and_condition_update, \
    terms_and_condition_delete
from products.selectors import tag_list, tag_get_by_slug, tag_get
from products.serializers import TypeSerializer
from products.services.tag_services import tag_create, tag_update, tag_delete
from users.permissions import IsSuperAdminOrStoreOwner


class TermsAndConditionListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        title = serializers.CharField()
        slug = serializers.CharField()
        description = serializers.CharField()
        type = serializers.CharField()

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        terms_and_conditions = terms_and_conditions_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=terms_and_conditions,
            request=request,
        )


class TermsAndConditionDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=True)
        language = serializers.CharField(required=True)
        translated_languages = serializers.JSONField(required=True)

    def get(self, request, slug):
        terms_and_condition = terms_and_conditions_get_by_slug(slug)

        if terms_and_condition is None:
            raise Http404

        data = self.OutputSerializer(terms_and_condition).data

        return Response(data)


class TermsAndConditionCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=True)
        description = serializers.CharField(required=True, allow_blank=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        terms_and_condition = terms_and_condition_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(terms_and_condition).data

        return Response(data)


class TermsAndConditionUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, terms_and_condition_id):
        serializer = TermsAndConditionCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        terms_and_condition = terms_and_conditions_get(terms_and_condition_id)

        if terms_and_condition is None:
            raise Http404

        tag = terms_and_condition_update(terms_and_condition=terms_and_condition, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = TermsAndConditionCreateApi.OutputSerializer(tag).data

        return Response(data)


class TermsAndConditionDeleteApi(APIView):
    @staticmethod
    def delete(request, terms_and_condition_id: str):
        terms_and_condition_delete(terms_and_condition_id=terms_and_condition_id)

        return Response(
            {"detail": "Terms and Condition successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
