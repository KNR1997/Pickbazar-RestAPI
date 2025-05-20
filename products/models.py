import uuid

from django.db import models

from common.models import BaseModel


def default_translated_languages():
    return ["en"]


# Create your models here.
class Type(BaseModel):
    name = models.CharField(max_length=20)
    slug = models.CharField(max_length=20, unique=True)
    banners = models.JSONField(default=list, blank=True, null=True)
    promotional_sliders = models.JSONField(default=list, blank=True, null=True)
    icon = models.CharField(max_length=20, default='default_icon', blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True,
                                            null=True)  # Add translated_languages field
    settings = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    details = models.TextField(null=True, blank=True)
    image = models.JSONField(default=list, blank=True, null=True)  # Assuming it's a JSON field
    icon = models.CharField(max_length=255, null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    icon = models.JSONField(default=dict, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.name


class Attribute(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)

    def __str__(self):
        return self.name


class AttributeValue(BaseModel):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    meta = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"


class Manufacturer(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    products_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    cover_image = models.JSONField(default=dict, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.name


class Author(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    products_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    bio = models.TextField(null=True, blank=True)
    languages = models.CharField(max_length=50)
    image = models.JSONField(default=dict, blank=True, null=True)
    cover_image = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.CharField(max_length=255, null=True, blank=True)
    height = models.CharField(max_length=255, null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    in_stock = models.BooleanField(default=True)
    is_taxable = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('publish', 'Publish'), ('draft', 'Draft')], default='publish')
    product_type = models.CharField(max_length=50, choices=[('variable', 'Variable'), ('simple', 'Simple')])
    unit = models.CharField(max_length=50, default='1 Stk', blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    gallery = models.JSONField(default=list, blank=True, null=True)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)

    type = models.ForeignKey(Type, blank=True, null=True, on_delete=models.SET_NULL, default=None)
    categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(Author, blank=True, null=True, on_delete=models.SET_NULL, default=None)
    manufacturer = models.ForeignKey(Manufacturer, blank=True, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.name


class ProductVariation(BaseModel):
    title = models.CharField(max_length=255)
    cartesian_product_key = models.CharField(max_length=255, null=True)
    barcode = models.CharField(max_length=15, unique=True, blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    default_quantity = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    attribute = models.ManyToManyField(Attribute, blank=True)
    value = models.ManyToManyField(AttributeValue, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.title}"


# class ProductVariationOption(BaseModel):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
#     variation = models.ForeignKey(ProductVariation, related_name='options', on_delete=models.CASCADE)
#     attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
#     value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
#
#     class Meta:
#         unique_together = ('variation', 'attribute', 'value')  # Enforce uniqueness
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.variation.product.name} - {self.attribute.name}: {self.value.value}"


class Batch(BaseModel):
    batch_number = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    received_date = models.DateField(blank=True, null=True)
    manufacture_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)  # For perishable goods
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    is_active = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)

    product = models.ForeignKey(Product, related_name='batches', on_delete=models.SET_NULL, null=True, blank=True)
    product_variation = models.ForeignKey(ProductVariation, related_name='variation_batches', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('product', 'batch_number')
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.batch_number} - {self.product.name if self.product else self.variation.product.name}"
