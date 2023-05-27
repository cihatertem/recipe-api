"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ("id",)
    list_display = ("email", "first_name", "last_name", "created_at")

    fieldsets = (
        (None, {
            "fields": (
                "email", "password", "first_name", "middle_name", "last_name"
            ),
        }),
        (_("Permissions"), {
            "fields": (
                "is_active", "is_staff", "is_superuser"
            )
        }),
        (_("Important Dates"), {
            "fields": (
                "last_login", "created_at", "updated_at"
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "first_name", "middle_name",
                "last_name", "is_active", "is_staff", "is_superuser"
            ),
        }),
    )

    readonly_fields = ("last_login", "created_at", "updated_at")


admin.site.register(models.User, UserAdmin)
