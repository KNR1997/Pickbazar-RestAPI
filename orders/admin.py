from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from orders.models import Order, OrderItem


# Register your models here.
@admin.register(Order)
class Order(ImportExportModelAdmin):
    pass


@admin.register(OrderItem)
class Type(ImportExportModelAdmin):
    pass
