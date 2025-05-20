from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from users.models import User, Address, Profile


@admin.register(User)
class User(ImportExportModelAdmin):
    pass


@admin.register(Address)
class Address(ImportExportModelAdmin):
    pass


@admin.register(Profile)
class Profile(ImportExportModelAdmin):
    pass
