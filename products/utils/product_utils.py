from django.db.models import Sum

from products.models import Product


def recalculate_product_total_quantity(product: Product) -> Product:
    """Recalculates and updates the total quantity of a Product based on its Batches."""
    total_quantity = product.batches.aggregate(total=Sum('quantity'))['total'] or 0
    product.quantity = total_quantity
    product.save(update_fields=['quantity'])
    return product
