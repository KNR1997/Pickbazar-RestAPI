from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query
from ecommerce.selectors import shipping_list, shipping_get
from ecommerce.services.shipping_services import shipping_create, shipping_update, shipping_delete
from users.permissions import IsSuperAdminOrStoreOwner


class ShippingListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        is_global = serializers.BooleanField()
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

        shipping = shipping_list(filters=filters_serializer.validated_data)

        # Serialize data
        serialized_taxes = self.OutputSerializer(shipping, many=True).data

        return Response(data=serialized_taxes)


class ShippingDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        name = serializers.CharField(required=True)
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        type = serializers.CharField(required=True)

    def get(self, request, shipping_id):
        shipping = shipping_get(shipping_id)

        if shipping is None:
            raise Http404

        data = self.OutputSerializer(shipping).data

        return Response(data)


class ShippingCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        type = serializers.CharField(required=True)
        amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        name = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping = shipping_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(shipping).data

        return Response(data)


class ShippingUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, shipping_id):
        serializer = ShippingCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping = shipping_get(shipping_id)

        if shipping is None:
            raise Http404

        shipping = shipping_update(shipping=shipping, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = ShippingCreateApi.OutputSerializer(shipping).data

        return Response(data)


class ShippingDeleteApi(APIView):
    @staticmethod
    def delete(request, shipping_id: str):
        shipping_delete(shipping_id=shipping_id)

        return Response(
            {"detail": "Shipping successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
