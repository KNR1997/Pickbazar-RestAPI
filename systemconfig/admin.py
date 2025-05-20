from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from systemconfig.models import Settings


# Register your models here.
@admin.register(Settings)
class Settings(ImportExportModelAdmin):
    pass
