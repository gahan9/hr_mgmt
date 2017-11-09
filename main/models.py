from django.contrib.auth.models import User
from django.db import models


class FileUpload(models.Model):
    # file_name = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='.', verbose_name="File")
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.file)


class EmployeeData(models.Model):
    user = models.OneToOneField(User, related_name="employee")
    contact_no = models.IntegerField(verbose_name="Mobile Number")

