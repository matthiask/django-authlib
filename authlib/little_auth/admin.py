from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin

from authlib.little_auth.models import User


@admin.register(User)
class UserAdmin(StockUserAdmin):
    fieldsets = None
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email",)
    search_fields = ("full_name", "email")
    filter_horizontal = ("groups", "user_permissions")
