from .models import *
import django_tables2 as tables


class FileUploadTable(tables.Table):
    class Meta:
        model = FileUpload
        attrs = {'class': 'table table-sm'}
