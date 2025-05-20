from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from layouts.selectors import faq_list, faq_get_by_slug, faq_get
from layouts.services.faq_services import faq_create, faq_update, faq_delete
from users.permissions import IsSuperAdminOrStoreOwner


class FaqListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        faq_title = serializers.CharField()
        slug = serializers.CharField()
        faq_description = serializers.CharField()
        faq_type = serializers.CharField()

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        faqs = faq_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=faqs,
            request=request,
        )


class FaqDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        faq_title = serializers.CharField(required=True)
        faq_description = serializers.CharField(required=True)
        translated_languages = serializers.JSONField()

    def get(self, request, slug):
        faq = faq_get_by_slug(slug)

        if faq is None:
            raise Http404

        data = self.OutputSerializer(faq).data

        return Response(data)


class FaqCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        faq_title = serializers.CharField(required=True)
        faq_description = serializers.CharField(required=True, allow_blank=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        faq = faq_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(faq).data

        return Response(data)


class FaqUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, faq_id):
        serializer = FaqCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        faq = faq_get(faq_id)

        if faq is None:
            raise Http404

        faq = faq_update(faq=faq, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = FaqCreateApi.OutputSerializer(faq).data

        return Response(data)


class FaqDeleteApi(APIView):
    @staticmethod
    def delete(request, faq_id: str):
        faq_delete(faq_id=faq_id)

        return Response(
            {"detail": "FAQ successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
