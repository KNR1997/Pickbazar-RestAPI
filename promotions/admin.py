from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from feedbacks.models import Review
from promotions.models import Coupon


# Register your models here.
@admin.register(Coupon)
class Coupon(ImportExportModelAdmin):
    pass


@admin.register(Review)
class Review(ImportExportModelAdmin):
    pass
