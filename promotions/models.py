import uuid

from django.db import models

from common.models import BaseModel


# Create your models here.
def default_translated_languages():
    return ["en"]


class Coupon(BaseModel):
    COUPON_TYPE = [
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.JSONField(default=dict, blank=True, null=True)
    type = models.CharField(max_length=50, choices=COUPON_TYPE)  # 'fixed', 'percentage', etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    minimum_cart_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    max_uses = models.PositiveIntegerField(blank=True, null=True)  # Optional maximum number of uses
    used_count = models.PositiveIntegerField(default=0)  # Track the number of times the discount has been used
    active_from = models.DateTimeField()
    expire_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)
    target = models.PositiveIntegerField(blank=True, null=True)
    is_approve = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)
    shop_id = models.PositiveIntegerField(blank=True, null=True)  # todo -> check for remove with front-end
    user_id = models.PositiveIntegerField(blank=True, null=True)  # todo -> check for remove with front-end

    def __str__(self):
        return self.code


class FlashSale(BaseModel):
    SALE_TYPE = [
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage')
    ]
    title = models.TextField()
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    type = models.CharField(max_length=50, choices=SALE_TYPE)  # 'fixed', 'percentage', etc.
    image = models.JSONField(default=dict, blank=True, null=True)
    cover_image = models.JSONField(default=dict, blank=True, null=True)
    language = models.CharField(max_length=10, default='en', blank=True, null=True)
    translated_languages = models.JSONField(default=default_translated_languages, blank=True, null=True)

    def __str__(self):
        return self.title
