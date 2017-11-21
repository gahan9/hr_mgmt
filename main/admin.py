from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import *


class UserModelAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('contact_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_hr', 'is_head_hr',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('contact_number', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'contact_number', 'first_name', 'last_name', 'email', 'is_hr', 'is_head_hr', 'is_staff', 'registration_date', 'password')
    search_fields = ('contact_number', 'first_name', 'last_name', 'email')
    ordering = ('-registration_date',)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_user', 'name', 'alternate_contact_no', 'alternate_email', 'country')


admin.site.register(UserModel, UserModelAdmin)
admin.site.register(Company, CompanyAdmin)

admin.site.site_header = 'FieldRate administration'
admin.site.site_title = 'FieldRate administration'
admin.site.index_title = 'FieldRate administration'
