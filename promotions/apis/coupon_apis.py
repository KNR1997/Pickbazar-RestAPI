import code

from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.selectors import tag_get_by_slug, tag_get
from products.services.tag_services import tag_update, tag_delete
from promotions.selectors import coupon_list, coupon_get_by_code, coupon_get
from promotions.services.coupon_services import coupon_create, coupon_update, coupon_delete
from users.permissions import IsSuperAdminOrStoreOwner


class CouponListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        code = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        code = serializers.CharField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        minimum_cart_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        active_from = serializers.CharField()
        expire_at = serializers.CharField()
        is_approve = serializers.BooleanField()

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        coupons = coupon_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=coupons,
            request=request,
        )


class CouponDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        code = serializers.CharField()
        type = serializers.CharField()
        description = serializers.CharField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        minimum_cart_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        active_from = serializers.CharField()
        expire_at = serializers.CharField()
        is_approve = serializers.BooleanField()
        language = serializers.CharField()
        translated_languages = serializers.JSONField()

    def get(self, request, code):
        coupon = coupon_get_by_code(code)

        if coupon is None:
            raise Http404

        data = self.OutputSerializer(coupon).data

        return Response(data)


class CouponCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        description = serializers.CharField(required=True, allow_null=True, allow_blank=True)
        image = serializers.JSONField(required=True)
        type = serializers.CharField(required=True)
        amount = serializers.IntegerField(required=True)
        minimum_cart_amount = serializers.IntegerField(required=True)
        active_from = serializers.DateTimeField(required=True)
        expire_at = serializers.DateTimeField(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = coupon_create(
            **serializer.validated_data
        )

        data = self.OutputSerializer(coupon).data

        return Response(data)


class CouponUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, coupon_id):
        serializer = CouponCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        coupon = coupon_get(coupon_id)

        if coupon is None:
            raise Http404

        coupon = coupon_update(coupon=coupon, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = CouponCreateApi.OutputSerializer(coupon).data

        return Response(data)


class CouponDeleteApi(APIView):
    @staticmethod
    def delete(request, coupon_id: str):
        coupon_delete(coupon_id=coupon_id)

        return Response(
            {"detail": "Coupon successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
