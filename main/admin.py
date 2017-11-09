from django.contrib import admin

from .models import *


class FileUploadAdmin(admin.ModelAdmin):
    search_fields = ['file']
    list_display = ('id', 'file')


admin.site.register(FileUpload, FileUploadAdmin)
