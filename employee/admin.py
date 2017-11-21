from django.contrib import admin
from django.shortcuts import redirect
from django.urls.base import reverse
from django.utils.translation import ugettext_lazy as _

from .models import *


class FileUploadAdmin(admin.ModelAdmin):
    search_fields = ['file']
    list_display = ('id', 'file')


class EmployeeDataAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_display = ('id', 'contact_number', 'first_name', 'last_name', 'company_name', 'email',
                    'alternate_email', 'alternate_contact_no', 'job_title',
                    'street', 'zip_code', 'city', 'country', 'is_head_hr', 'is_hr', 'registration_date'
                    )
    ordering = ('company_name', '-registration_date', )

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     print(object_id)
    #     print(Employee.objects.get(id=object_id).user.id)
    #     return redirect(
    #         "admin:main_usermodel_change",
    #         args=(Employee.objects.get(id=object_id).user.id,)
    #     )

    @staticmethod
    def contact_number(obj):
        return obj.user.contact_number

    @staticmethod
    def is_head_hr(obj):
        return obj.user.is_head_hr

    @staticmethod
    def is_hr(obj):
        return obj.user.is_hr

    @staticmethod
    def first_name(obj):
        return obj.user.first_name

    @staticmethod
    def last_name(obj):
        return obj.user.last_name

    @staticmethod
    def email(obj):
        return obj.user.email


class QuestionDBAdmin(admin.ModelAdmin):
    search_fields = ['question']
    list_display = ('question', 'answer_type')


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_region')

    def employee_region(self, obj):
        return obj.employee_group.region


admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(Employee, EmployeeDataAdmin)
