"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    """
    Define admin pages for users.
    """
    ordering: tuple = ('id',)
    list_display: tuple = ('email', 'name')
    fieldsets: tuple = (
        (
            _('Account Information'),
            {
                'fields': (
                    'email',
                    'password',
                    'name'
                )
            }
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (
            _('Important Dates'),
            {
                'fields': ('last_login',)
            }
        )
    )
    readonly_fields: tuple = ('last_login',)

    add_fieldsets: tuple = (
        (
            _('Add A New User'),
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
