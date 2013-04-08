"""
Django admin overrides for the IX profile server client.
"""
from django.forms import fields
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import User

from ixprofile_client import forms


class AdminUserChangeForm(forms.UserChangeForm):
    """
    A form for editing the user in the admin interface.
    """
    is_staff = fields.BooleanField(required=False)
    is_superuser = fields.BooleanField(required=False)


# pylint:disable=R0904
# Too many public methods - in the base class
class UserAdmin(auth_admin.UserAdmin):
    """
    Customised version of the user admin.
    """
    fieldsets = (
        (None, {'fields': (
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',
        )}),
    )

    add_fieldsets = (
        (None, {'fields': (
            'email',
            'first_name',
            'last_name',
        )}),
    )

    edit_readonly_fields = (
        'email',
        'first_name',
        'last_name',
    )

    readonly_fields = (
        'last_login',
        'date_joined',
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )

    def get_readonly_fields(self, request, user=None):
        """
        Only allow certain fields to be editable on creation.
        """
        if user and user.pk:
            return self.edit_readonly_fields + self.readonly_fields
        else:
            return self.readonly_fields

    form = AdminUserChangeForm
    add_form = forms.UserCreationForm

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
