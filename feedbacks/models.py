import uuid

from django.db import models

from common.models import BaseModel
from orders.models import Order
from products.models import Product, ProductVariation


# Create your models here.
class Review(BaseModel):
    comment = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField()
    positive_feedbacks_count = models.PositiveIntegerField(default=0)
    negative_feedbacks_count = models.PositiveIntegerField(default=0)
    abusive_reports_count = models.PositiveIntegerField(default=0)

    order = models.ForeignKey(Order, blank=False, null=False, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariation, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order-{self.order}"
