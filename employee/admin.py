"""
FieldRate Administration- will only be accessible by Super User
individual company can not access this features
super user can manage all companies data(for which model admin are registered here)
"""
from django.contrib import admin
from .models import *


class FileUploadAdmin(admin.ModelAdmin):
    """
    mange file upload details
    """
    search_fields = ['file']
    list_display = ('id', 'file')


class EmployeeDataAdmin(admin.ModelAdmin):
    """
    every employee detail registered in field-rate from all companies
    """
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
    """
    manage questions of all companies
    """
    search_fields = ['question']
    list_display = ('id', 'question', 'answer_type', 'content_type', 'used_by')

    @staticmethod
    def used_by(obj):
        return ", ".join([a.first_name for a in obj.asked_by.all()])


class SurveyAdmin(admin.ModelAdmin):
    """
    manage surveys of all companies
    """
    list_display = ('id', 'name', 'employee_group', 'get_question', 'steps', 'start_date', 'end_date', 'complete')


class MCQAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'option', 'rel_type')

    @staticmethod
    def rel_type(obj):
        if obj.type.all():
            return obj.type.all()[0]
        else:
            return "-"


class RatingAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'rate_value')


class TextAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')


admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(Employee, EmployeeDataAdmin)
admin.site.register(QuestionDB, QuestionDBAdmin)
admin.site.register(MCQAnswer, MCQAnswerAdmin)
admin.site.register(RatingAnswer, RatingAnswerAdmin)
admin.site.register(TextAnswer, TextAnswerAdmin)
admin.site.register(Survey, SurveyAdmin)
