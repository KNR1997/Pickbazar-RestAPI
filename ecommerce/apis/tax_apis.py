from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from ecommerce.selectors import tax_list, tax_get
from ecommerce.services.tax_services import tax_create, tax_update, tax_delete
from layouts.selectors import faq_list, faq_get_by_slug, faq_get
from layouts.services.faq_services import faq_create, faq_update, faq_delete
from products.selectors import tag_get
from users.permissions import IsSuperAdminOrStoreOwner


class TaxListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        country = serializers.CharField()
        state = serializers.CharField()
        zip = serializers.CharField()
        city = serializers.CharField()
        name = serializers.CharField()
        rate = serializers.DecimalField(max_digits=5, decimal_places=2)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        taxes = tax_list(filters=filters_serializer.validated_data)

        # Serialize data
        serialized_taxes = self.OutputSerializer(taxes, many=True).data

        return Response(data=serialized_taxes)


class TaxDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        rate = serializers.CharField(required=True)
        country = serializers.CharField()
        city = serializers.CharField()
        state = serializers.CharField()
        zip = serializers.CharField()

    def get(self, request, tax_id):
        tax = tax_get(tax_id)

        if tax is None:
            raise Http404

        data = self.OutputSerializer(tax).data

        return Response(data)


class TaxCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        rate = serializers.CharField(required=True)
        country = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        city = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        state = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        zip = serializers.CharField(required=True, allow_blank=True, allow_null=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tax = tax_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(tax).data

        return Response(data)


class TaxUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, tax_id):
        serializer = TaxCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tax = tax_get(tax_id)

        if tax is None:
            raise Http404

        tax = tax_update(tax=tax, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = TaxCreateApi.OutputSerializer(tax).data

        return Response(data)


class TaxDeleteApi(APIView):
    @staticmethod
    def delete(request, tax_id: str):
        tax_delete(tax_id=tax_id)

        return Response(
            {"detail": "Tax successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
