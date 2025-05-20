from django.db import models

from common.models import BaseModel


# Create your models here.
class Tax(BaseModel):
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    name = models.CharField(max_length=255)
    is_global = models.BooleanField(default=False)
    priority = models.IntegerField(null=True, blank=True)
    on_shipping = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class Shipping(BaseModel):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_global = models.BooleanField(default=False)
    type = models.CharField(max_length=50, choices=[('fixed', 'Fixed'), ('variable', 'Variable')])

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.type})"
