from typing import List

from django.db import transaction

from common.services import model_update
from common.utils import get_object
from products.models import Product, Batch, ProductVariation
from products.selectors import attribute_value_get
from products.services.batch_services import batch_create
from products.utils.product_utils import recalculate_product_total_quantity


@transaction.atomic
def product_create_process(*, name: str,
                           slug: str,
                           description: str = None,
                           product_type: str = None,
                           type: str,
                           categories: list = None,
                           tags: list = None,
                           batches: object = None,
                           author_id: str = None,
                           manufacturer_id: str = None,
                            variations: list = None,
                           variation_options: object,
                           ) -> Product:
    product = product_create(name=name,
                             slug=slug,
                             description=description,
                             product_type=product_type,
                             type=type,
                             categories=categories,
                             tags=tags,
                             batches=batches,
                             author_id=author_id,
                             manufacturer_id=manufacturer_id,
                             )

    if product_type == 'variable':
        variation_options_upsert = variation_options.get('upsert')
        for variation_option in variation_options_upsert:
            product_variation_create(product=product,
                                     title=variation_option.get('title'),
                                     # quantity=variation_option.get('quantity'),
                                     cartesian_product_key=variation_option.get('cartesian_product_key'),
                                     barcode=variation_option.get('barcode'),
                                     default_quantity=variation_option.get('default_quantity'),
                                     variations=variations,
                                     )
    return product


@transaction.atomic
def product_create(*, name: str,
                   slug: str,
                   description: str = None,
                   product_type: str = None,
                   type: str,
                   categories: list = None,
                   tags: list = None,
                   batches: object = None,
                   author_id: str = None,
                   manufacturer_id: str = None,
                   ) -> Product:
    product = Product.objects.create(name=name,
                                     slug=slug,
                                     description=description,
                                     product_type=product_type,
                                     type_id=type,
                                     author_id=author_id,
                                     manufacturer_id=manufacturer_id,
                                     )

    # Add categories to the product
    if categories:
        for category in categories:
            product.categories.add(category)  # Assuming categories are instances or IDs

    # Add tags to the product
    if tags:
        for tag in tags:
            product.tags.add(tag)  # Assuming tags are instances or IDs

    # Create Batches
    if batches:
        batch_upsert = batches.get('upsert')
        if batch_upsert:
            for batch in batch_upsert:
                batch_create(product=product,
                             batch_number=batch.get('batch_number'),
                             quantity=batch.get('quantity'),
                             manufacture_date=batch.get('manufacture_date'),
                             expiry_date=batch.get('expiry_date'),
                             cost=batch.get('cost'),
                             price=batch.get('price'),
                             sale_price=batch.get('sale_price'),
                             )

    return product


@transaction.atomic
def product_update(*, product: Product, data) -> Product:
    non_side_effect_fields: List[str] = [
        "name",
        "slug",
        "description",
        "image",
        "gallery",
        "unit",
        "sku",
        "price",
        "sale_price",
        "height",
        "width",
    ]

    product, has_updated = model_update(instance=product, fields=non_side_effect_fields, data=data)

    # Update batches if provided
    if "batches" in data:
        batches = data["batches"]

        # Handle upsert batches
        batch_upsert = batches.get("upsert", [])
        for batch in batch_upsert:
            batch_instance = Batch.objects.filter(batch_number=batch.get("batch_number"), product=product).first()
            if batch_instance:
                # Update existing batch
                model_update(instance=batch_instance, fields=[
                    "quantity", "manufacture_date", "expiry_date", "cost", "price", "sale_price"
                ], data=batch)
            else:
                # Create new batch
                batch_create(product=product,
                             batch_number=batch.get("batch_number"),
                             quantity=batch.get("quantity"),
                             manufacture_date=batch.get("manufacture_date"),
                             expiry_date=batch.get("expiry_date"),
                             cost=batch.get("cost"),
                             price=batch.get("price"),
                             sale_price=batch.get("sale_price"),
                             )

        # Handle delete batches
        batch_delete = batches.get("delete", [])
        for batch_id in batch_delete:
            Batch.objects.filter(pk=batch_id, product=product).delete()

    # some additional task
    product.type_id = data.get("type")
    product.save()

    # Recalculate Product quantity based of all the Batches it has
    recalculate_product_total_quantity(product=product)

    return product


@transaction.atomic
def product_delete(*, product_id: str) -> None:
    product = get_object(Product, id=product_id)
    product.delete()
    return None


@transaction.atomic
def product_variation_create(
        *, product: Product,
        title: str,
        cartesian_product_key: str,
        barcode: str = None,
        default_quantity: int = None,
        attributes: list = None,
        values: list = None,
        variations: list,
) -> ProductVariation:
    product_variation = ProductVariation.objects.create(product=product,
                                                        title=title,
                                                        cartesian_product_key=cartesian_product_key,
                                                        barcode=barcode,
                                                        default_quantity=default_quantity,
                                                        )
    if variations:
        for variation in variations:
            attribute_value = attribute_value_get(variation.get('attribute_value_id'))
            # Add attributes like Color, Size etc.
            product_variation.attribute.add(attribute_value.attribute)
            # Add attribute values like red, small etc.
            product_variation.value.add(attribute_value)

    return product_variation
