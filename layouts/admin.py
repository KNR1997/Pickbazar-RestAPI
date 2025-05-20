from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from layouts.models import FAQ, TermsAndConditions


# Register your models here.
@admin.register(FAQ)
class FAQ(ImportExportModelAdmin):
    pass


@admin.register(TermsAndConditions)
class TermsAndConditions(ImportExportModelAdmin):
    pass
