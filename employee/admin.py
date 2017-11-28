from django.contrib import admin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from .models import *


class FileUploadAdmin(admin.ModelAdmin):
    search_fields = ['file']
    list_display = ('id', 'file')


class EmployeeDataAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_display = ('id', 'contact_number', 'first_name', 'last_name', 'company_name', 'email', 'role',
                    # 'alternate_email', 'alternate_contact_no',
                    'job_title',
                    # 'street', 'zip_code', 'city',
                    'country', 'added_by', 'registration_date'
                    )
    ordering = ('company_name', '-registration_date', )

    @staticmethod
    def contact_number(obj):
        return obj.user.contact_number

    @staticmethod
    def role(obj):
        return obj.user.role

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

    @staticmethod
    def employee_region(obj):
        return obj.employee_group.region


admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(Employee, EmployeeDataAdmin)
admin.site.register(QuestionDB, QuestionDBAdmin)
admin.site.register(MCQAnswer)
admin.site.register(RatingAnswer)
admin.site.register(TextAnswer)
