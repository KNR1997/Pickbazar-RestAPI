import uuid

from django.db import models

from common.models import BaseModel
from products.models import Product, ProductVariation, Batch


# Create your models here.
class Order(BaseModel):
    PAYMENT_GATEWAYS = [
        ('CASH', 'Cash'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
        ('CREDIT_CARD', 'Credit Card'),
        ('PAYPAL', 'PayPal'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]

    ORDER_STATUSES = [
        ('order-pending', 'Order Pending'),
        ('order-processing', 'Order Processing'),
        ('order-completed', 'Order Completed'),
        ('order-cancelled', 'Order Cancelled'),
    ]

    PAYMENT_STATUSES = [
        ('payment-pending', 'Payment Pending'),
        ('payment-completed', 'Payment Completed'),
        ('payment-failed', 'Payment Failed'),
    ]

    tracking_number = models.CharField(max_length=50, unique=True)
    customer_id = models.IntegerField()
    customer_contact = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sales_tax = models.DecimalField(max_digits=10, decimal_places=2)
    paid_total = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    cancelled_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cancelled_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cancelled_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    language = models.CharField(max_length=10, default='en')
    coupon_id = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    shop_id = models.IntegerField(blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_gateway = models.CharField(max_length=50, choices=PAYMENT_GATEWAYS, default='CASH_ON_DELIVERY')
    altered_payment_gateway = models.CharField(max_length=50, blank=True, null=True)
    logistics_provider = models.CharField(max_length=255, blank=True, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_time = models.CharField(max_length=255, blank=True, null=True)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUSES, default='order-pending')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUSES, default='payment-pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wallet_point = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Order {self.tracking_number} - {self.customer_name}"


class OrderItem(BaseModel):
    batch_number = models.CharField(max_length=50, blank=True, null=True)  # Added batch number
    item_name = models.CharField(max_length=200, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    percentage_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    sale_price_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    percentage_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    flat_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    quantity = models.IntegerField(blank=True, default=1)
    return_quantity = models.IntegerField(default=0)
    item_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    item_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    order = models.ForeignKey(Order, blank=False, null=False, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    product_variant = models.ForeignKey(ProductVariation, blank=True, null=True, on_delete=models.SET_NULL)
    batch = models.ForeignKey(Batch, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Order-{self.order}"
