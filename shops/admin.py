from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from shops.models import Shop


# Register your models here.
@admin.register(Shop)
class Shop(ImportExportModelAdmin):
    pass
