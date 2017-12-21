from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import *


class UserModelAdmin(UserAdmin):
    """ Model Admin to handle custom user model by Super User"""
    fieldsets = (
        (None, {'fields': ('contact_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'profile_image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('contact_number', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'contact_number', 'first_name', 'last_name', 'email', 'role', 'is_staff',
                    # 'profile_image', 'password',
                    'registration_date',
                    )
    search_fields = ('contact_number', 'first_name', 'last_name', 'email')
    ordering = ('-registration_date',)


class PlanAdmin(admin.ModelAdmin):
    """ Manage/view/add plans """
    list_display = ['id', 'plan_name', 'plan_price', 'plan_validity']


class CompanyAdmin(admin.ModelAdmin):
    """ View/Manage companies from admin """
    list_display = ('id', 'company_user', 'name', 'alternate_contact_no', 'alternate_email', 'country')
    search_fields = ['id', 'name', 'alternate_contact_no', 'alternate_email', 'country']


class ActivityMonitorAdmin(admin.ModelAdmin):
    """ Manage log of activity performed by company admin """
    search_fields = ['performed_by', 'activity_type', 'affected_user']
    list_display = ('id', 'company', 'performed_by', 'activity_type', 'affected_user', 'bulk_create',
                    'status', 'remarks', 'time_stamp')


admin.site.register(UserModel, UserModelAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(ActivityMonitor, ActivityMonitorAdmin)

admin.site.site_header = 'FieldRate administration'
admin.site.site_title = 'FieldRate administration'
admin.site.index_title = 'FieldRate administration'
