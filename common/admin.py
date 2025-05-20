from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from common.models import ErrorLog, AuditLog, APIActivityLog


# Register your models here.
@admin.register(AuditLog)
class AuditLog(ImportExportModelAdmin):
    pass


@admin.register(APIActivityLog)
class APIActivityLogAdmin(admin.ModelAdmin):
    list_display = ["token_identifier", "path", "method", "response_code", "ip_address", "created_at"]
    search_fields = ["path", "token_identifier", "method"]
    list_filter = ["method", "response_code"]


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "path", "status_code", "exception_type", "user")
    search_fields = ("message", "stack_trace", "path", "exception_type")
    list_filter = ("status_code", "exception_type")
