from typing import Optional

from django.db.models import QuerySet

from common.utils import get_object
from products.filters import BaseCategoryFilter, BaseProductFilter
from products.models import Type, Tag, Category, Attribute, Manufacturer, Author, Product, AttributeValue, Batch, \
    ProductVariation


def type_list(*, filters=None) -> QuerySet[Type]:
    filters = filters or {}

    qs = Type.objects.all()

    return qs


def type_get(type_id) -> Optional[Type]:
    type_ = get_object(Type, id=type_id)

    return type_


def type_get_by_slug(slug) -> Optional[Type]:
    type_ = get_object(Type, slug=slug)

    return type_


def tag_list(*, filters=None) -> QuerySet[Tag]:
    filters = filters or {}

    qs = Tag.objects.all()

    return qs

def tag_get(tag_id) -> Optional[Tag]:
    tag = get_object(Tag, id=tag_id)

    return tag


def tag_get_by_slug(slug) -> Optional[Tag]:
    tag = get_object(Tag, slug=slug)

    return tag

def category_list(*, filters=None) -> QuerySet[Category]:
    filters = filters or {}

    qs = Category.objects.all()

    return BaseCategoryFilter(filters, qs).qs


def category_get_by_slug(slug) -> Optional[Category]:
    category = get_object(Category, slug=slug)

    return category


def category_get(category_id) -> Optional[Category]:
    category = get_object(Category, id=category_id)

    return category


def attribute_list(*, filters=None) -> QuerySet[Attribute]:
    filters = filters or {}

    qs = Attribute.objects.all()

    return qs


def attribute_get_by_slug(slug) -> Optional[Attribute]:
    attribute = get_object(Attribute, slug=slug)

    return attribute


def attribute_get(attribute_id) -> Optional[Attribute]:
    attribute = get_object(Attribute, id=attribute_id)

    return attribute


def manufacturer_list(*, filters=None) -> QuerySet[Manufacturer]:
    filters = filters or {}

    qs = Manufacturer.objects.all()

    return qs


def manufacturer_get_by_slug(slug) -> Optional[Manufacturer]:
    manufacturer = get_object(Manufacturer, slug=slug)

    return manufacturer


def author_list(*, filters=None) -> QuerySet[Author]:
    filters = filters or {}

    qs = Author.objects.all()

    return qs


def author_get_by_slug(slug) -> Optional[Author]:
    author = get_object(Author, slug=slug)

    return author


def product_list(*, filters=None) -> QuerySet[Product]:
    filters = filters or {}

    qs = Product.objects.all()

    return BaseProductFilter(filters, qs).qs


def product_get(tag_id) -> Optional[Product]:
    product = get_object(Product, id=tag_id)

    return product


def product_get_by_slug(slug) -> Optional[Product]:
    product = get_object(Product, slug=slug)

    return product


def attribute_value_get(attribute_value_id) -> Optional[AttributeValue]:
    attribute_value = get_object(AttributeValue, id=attribute_value_id)

    return attribute_value


def batch_get(batch_id) -> Optional[Batch]:
    batch = get_object(Batch, id=batch_id)

    return batch
