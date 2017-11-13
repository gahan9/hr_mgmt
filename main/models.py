from django.contrib.auth.models import User
from django.db import models
import django_filters


class FileUpload(models.Model):
    # file_name = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='.', verbose_name="File")
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.file)

    class Meta:
        verbose_name = "Uploaded file"
        verbose_name_plural = "Uploaded files"


class EmployeeData(models.Model):
    user = models.OneToOneField(User, related_name="employee")
    contact_no = models.CharField(max_length=15, verbose_name="Mobile Number")
    registration_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.user.first_name)

    class Meta:
        verbose_name = "Employee Detail"
        verbose_name_plural = "Employee Details"


class QuestionDB(models.Model):
    CHOICE = [(0, "Rating"), (1, "ShortTextField"), (2, "LongTextField")]
    question = models.TextField()
    answer_type = models.IntegerField(choices=CHOICE)

    class Meta:
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Bank"


class EmployeeDataFilter(django_filters.FilterSet):
    # user__first_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EmployeeData
        fields = ['user__first_name']
