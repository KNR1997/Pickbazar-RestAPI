from rest_framework import serializers

from products.models import Type, Category, Tag, Author, Manufacturer, AttributeValue, Batch, Attribute, \
    ProductVariation


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = '__all__'


class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = '__all__'


class AttributeValueWithAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer()

    class Meta:
        model = AttributeValue
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = '__all__'
