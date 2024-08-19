from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.utils.translation import gettext_lazy as _

from authlib.little_auth.models import User


@admin.register(User)
class UserAdmin(StockUserAdmin):
    add_fieldsets = (
        (None, {"classes": ["wide"], "fields": ("email", "password1", "password2")}),
    )
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "is_active",
                    "email",
                    "password",
                    "full_name",
                ]
            },
        ),
        (
            _("Permissions"),
            {
                "fields": [
                    "is_staff",
                    "is_superuser",
                    "role",
                ]
            },
        ),
        (
            _("Advanced"),
            {
                "classes": ["collapse"],
                "fields": [
                    "date_joined",
                    "last_login",
                    "groups",
                ],
            },
        ),
    ]
    list_display = (
        "email",
        "full_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "role",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "role", "groups")
    ordering = ("email",)
    search_fields = ("full_name", "email")
    filter_horizontal = ("groups", "user_permissions")
    radio_fields = {"role": admin.VERTICAL}
    readonly_fields = ["last_login"]
