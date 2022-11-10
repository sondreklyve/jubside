from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import ugettext, ugettext_lazy as _


class UserFieldAdmin(UserAdmin):
    list_display = ('email', 'date_joined', 'first_name', 'last_name', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'starting_year', 'allergies')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        ('Brukerstatus', {'fields': ('is_awaiting_approval','account_verified')}),
    )


admin.site.register(User, UserFieldAdmin)