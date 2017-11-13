from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib import admin

from .models import *


class FileUploadAdmin(admin.ModelAdmin):
    search_fields = ['file']
    list_display = ('id', 'file')


class EmployeeDataAdmin(admin.ModelAdmin):
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_display = ('id', 'first_name', 'last_name', 'email', 'contact_no', 'registration_date')

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def email(self, obj):
        return obj.user.email


class QuestionDBAdmin(admin.ModelAdmin):
    search_fields = ['question']
    list_display = ('question', 'answer_type')


admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(EmployeeData, EmployeeDataAdmin)
admin.site.register(QuestionDB, QuestionDBAdmin)

admin.site.site_header = 'FieldRate administration'
admin.site.site_title = 'FieldRate administration'
admin.site.index_title = 'FieldRate administration'
