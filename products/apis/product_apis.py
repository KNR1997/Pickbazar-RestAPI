from django.db import transaction
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import parse_search_query, get_paginated_response
from products.models import AttributeValue
from products.selectors import product_list, product_get_by_slug
from products.serializers import TypeSerializer, CategorySerializer, TagSerializer, ManufacturerSerializer, \
    AuthorSerializer, BatchSerializer, AttributeValueSerializer, AttributeValueWithAttributeSerializer, \
    ProductVariationSerializer
from products.services.product_services import product_create, product_delete, product_update, product_create_process


class ProductListApi(APIView):
    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        slug = serializers.CharField()
        status = serializers.CharField()
        product_type = serializers.CharField()
        price = serializers.DecimalField(max_digits=10, decimal_places=2)
        quantity = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get(self, request):
        # Extract `search` query parameter
        query_params = request.query_params
        search_query = query_params.get("search", None)

        # Parse `search` using the utility function
        filters = parse_search_query(search_query)

        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data={**request.query_params, **filters})
        filters_serializer.is_valid(raise_exception=True)

        products = product_list(filters=filters_serializer.validated_data)

        # Apply pagination
        return get_paginated_response(
            serializer_class=self.OutputSerializer,
            queryset=products,
            request=request,
        )


class ProductDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField()
        name = serializers.CharField()
        slug = serializers.CharField()
        unit = serializers.CharField()
        description = serializers.CharField()
        status = serializers.CharField()
        product_type = serializers.CharField()
        language = serializers.CharField()
        translated_languages = serializers.JSONField()
        sku = serializers.CharField()
        price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        sale_price = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
        height = serializers.CharField()
        width = serializers.CharField()
        image = serializers.JSONField()
        gallery = serializers.JSONField()

        type = TypeSerializer(required=False)
        categories = CategorySerializer(required=False, many=True)
        tags = TagSerializer(many=True)
        author = AuthorSerializer()
        manufacturer = ManufacturerSerializer()
        batches = BatchSerializer(many=True)
        variations = serializers.SerializerMethodField()
        variation_options = serializers.SerializerMethodField()

        def get_variations(self, obj):
            # Get all related ProductVariation instances
            variations = obj.variations.all()
            # Collect all AttributeValue objects from each variation
            attribute_values = AttributeValue.objects.filter(productvariation__in=variations).distinct()
            return AttributeValueWithAttributeSerializer(attribute_values, many=True).data

        def get_variation_options(self, obj):
            # Get all related ProductVariation instances
            variations = obj.variations.all()
            return ProductVariationSerializer(variations, many=True).data

    def get(self, request, slug):
        product = product_get_by_slug(slug)

        if product is None:
            raise Http404

        data = self.OutputSerializer(product).data

        return Response(data)


class BatchInputSerializer(serializers.Serializer):
    upsert = serializers.ListField(
        child=serializers.DictField(),  # Define the structure of items in the "upsert" list
        default=list
    )
    delete = serializers.ListField(
        child=serializers.CharField(),  # Batch ids or unique identifiers as strings
        default=list
    )


class VariationInputSerializer(serializers.Serializer):
    attribute_value_id = serializers.CharField(required=True)


class VariationOptionInputSerializer(serializers.Serializer):
    upsert = serializers.ListField(
        child=serializers.DictField(),  # Define the structure of items in the "upsert" list
        default=list
    )
    delete = serializers.ListField(
        child=serializers.CharField(),  # Batch ids or unique identifiers as strings
        default=list
    )


class ProductCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(required=True)
        slug = serializers.CharField(required=True)
        description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        product_type = serializers.CharField(required=True)
        type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        categories = serializers.ListField(child=serializers.CharField(required=True))
        tags = serializers.ListField(child=serializers.CharField(required=True))
        author_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        manufacturer_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        # sku = serializers.CharField(required=True)
        # price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)
        # sale_price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2, allow_null=True)
        height = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        width = serializers.CharField(required=False, allow_blank=True, allow_null=True)
        batches = BatchInputSerializer(required=False)
        variations = VariationInputSerializer(required=False, many=True)
        variation_options = VariationOptionInputSerializer(required=True)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        slug = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = product_create_process(
            **serializer.validated_data
        )

        data = self.OutputSerializer(product).data

        return Response(data)


class ProductUpdateApi(APIView):

    @transaction.atomic
    def put(self, request, slug):
        serializer = ProductCreateApi.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = product_get_by_slug(slug)

        if product is None:
            raise Http404

        product = product_update(product=product, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = ProductCreateApi.OutputSerializer(product).data

        return Response(data)


class ProductDeleteApi(APIView):
    @staticmethod
    def delete(request, product_id: str):
        product_delete(product_id=product_id)

        return Response(
            {"detail": "Product successfully deleted."},
            status=status.HTTP_204_NO_CONTENT  # 204 for successful delete with no content
        )
