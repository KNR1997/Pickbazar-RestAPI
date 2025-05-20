from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from orders.selectors import order_list, order_get
from orders.serializers import OrderItemSerializer
from orders.services.order_services import order_create_process, order_update, shop_order_create_process
from products.selectors import tag_get_by_slug, tag_get
from products.services.tag_services import tag_create, tag_update, tag_delete
from users.permissions import IsSuperAdminOrStoreOwner


class OrderListApi(APIView):
    permission_classes = [IsSuperAdminOrStoreOwner]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        tracking_number = serializers.CharField()
        order_status = serializers.CharField()
        total = serializers.CharField()
        created_at = serializers.CharField()

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        orders = order_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=orders,
            request=request,
        )


class OrderDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        tracking_number = serializers.CharField()
        order_status = serializers.CharField()
        total = serializers.CharField()
        payment_status = serializers.CharField()
        created_at = serializers.CharField()
        payment_gateway = serializers.CharField()
        order_items = OrderItemSerializer(many=True)

    def get(self, request, order_id):
        order = order_get(order_id)

        if order is None:
            raise Http404

        data = self.OutputSerializer(order).data

        return Response(data)


class ProductInputSerializer(serializers.Serializer):
    order_quantity = serializers.IntegerField(required=False)  # Include if updating an existing address
    product_id = serializers.UUIDField(required=True)
    subtotal = serializers.IntegerField(required=True)
    unit_price = serializers.IntegerField(default=False)


class OrderCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        amount = serializers.IntegerField(required=True)
        # billing_address	 = serializers.IntegerField(required=True)
        coupon_id = serializers.UUIDField(required=True, allow_null=True)
        customer_contact = serializers.CharField(required=True, allow_null=True)
        customer_id = serializers.CharField(required=True, allow_null=True)
        delivery_fee = serializers.IntegerField(required=True, allow_null=True)
        delivery_time = serializers.CharField(required=True, allow_null=True)
        discount = serializers.IntegerField(required=True)
        paid_total = serializers.IntegerField(required=True)
        payment_gateway = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        products = serializers.ListSerializer(child=ProductInputSerializer())
        sales_tax = serializers.IntegerField(required=True)
        # shipping_address		 = serializers.IntegerField(required=True)
        total = serializers.IntegerField(required=True)
        use_wallet_points = serializers.BooleanField(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        # slug = serializers.CharField(required=True)

    @transaction.atomic
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = order_create_process(
            **serializer.validated_data
        )

        data = self.OutputSerializer(order).data

        return Response(data)


class ShopOrderCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        # amount = serializers.IntegerField(required=True)
        # # billing_address	 = serializers.IntegerField(required=True)
        # coupon_id = serializers.UUIDField(required=True, allow_null=True)
        # customer_contact = serializers.CharField(required=True, allow_null=True)
        # customer_id = serializers.CharField(required=True, allow_null=True)
        # delivery_fee = serializers.IntegerField(required=True, allow_null=True)
        # delivery_time = serializers.CharField(required=True, allow_null=True)
        # discount = serializers.IntegerField(required=True)
        # paid_total = serializers.IntegerField(required=True)
        # payment_gateway = serializers.CharField(required=True, allow_blank=True, allow_null=True)
        products = serializers.ListSerializer(child=ProductInputSerializer())
        # sales_tax = serializers.IntegerField(required=True)
        # # shipping_address		 = serializers.IntegerField(required=True)
        # total = serializers.IntegerField(required=True)
        # use_wallet_points = serializers.BooleanField(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        # slug = serializers.CharField(required=True)

    @transaction.atomic
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = request.user

        order = shop_order_create_process(
            customer=customer,
            **serializer.validated_data
        )

        data = self.OutputSerializer(order).data

        return Response(data)


class OrderUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        order_status = serializers.CharField(required=False)

    @transaction.atomic
    def put(self, request, order_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = order_get(order_id)

        if order is None:
            raise Http404

        order = order_update(order=order, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = OrderCreateApi.OutputSerializer(order).data

        return Response(data)


class OrderDeleteApi(APIView):
    @staticmethod
    def delete(request, tag_id: str):
        tag_delete(tag_id=tag_id)

        return Response(
            {"detail": "Tag successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )


class OrderCheckoutVerifyApi(APIView):

    @transaction.atomic
    def post(self, request):
        try:
            data = {
                "total_tax": 0,
                "shipping_charge": 0,
                "unavailable_products": [],
                "wallet_currency": 0,
                "wallet_amount": 0,
            }

            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
