import hashlib
import os

from django import forms
from django.contrib.auth.hashers import make_password
from django.db.models import FileField
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


def computeMD5hash(my_string):
    """
    Encrypt plaintext to md5 checksum
    :param my_string:
    :return:
    """
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


def set_password_hash(password):
    return make_password(computeMD5hash(password))


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types")
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep file size under %s. Current file size %s') % (
                    filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass
        return data


def generate_dump():
    """
    fixtures : ['employee.json', 'fileupload.json', 'newsfeed.json', 'questiondb.json', 'survey.json', 'surveyresponse.json', 'company.json', 'usermodel.json', 'plan.json', 'activitymonitor.json']
    :return:
    """
    employee_tables = ["employee", "fileupload", "newsfeed", "questiondb", "survey", "surveyresponse"]
    main_tables = ["company", "usermodel", "plan", "activitymonitor"]
    base_cmd = "/usr/bin/python3 manage.py dump_object {} '*' > {}.json"
    db = [("employee." + i, i) for i in employee_tables]
    db += [("main." + i, i) for i in main_tables]
    db_lis = []
    for i in db:
        _path = os.path.join("/home/quixom/Project/employee_management/employee/fixtures", i[1])
        db_lis.append(i[1] + ".json")
        _cmd = base_cmd.format(i[0], _path)
        os.popen(_cmd)
    return db_lis

