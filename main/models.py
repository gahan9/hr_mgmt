from django.contrib.auth.models import User
from django.db import models
from .utility import ContentTypeRestrictedFileField
from django_countries.fields import CountryField


class FileUpload(models.Model):
    # file = ContentTypeRestrictedFileField(
    #     upload_to='.', verbose_name="File", max_upload_size=5242880,
    #     content_types=['text/csv'],
    # )
    file = models.FileField(upload_to='.', verbose_name="File")
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.file)

    class Meta:
        verbose_name = "Uploaded file"
        verbose_name_plural = "Uploaded files"


class EmployeeData(models.Model):
    user = models.OneToOneField(User, related_name="employee")
    contact_no = models.CharField(max_length=15, verbose_name="Mobile Number", unique=True)
    registration_date = models.DateTimeField(auto_now=True)
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True, verbose_name="Alternate Contact Number")
    job_title = models.CharField(max_length=30, verbose_name="Job Title", blank=True)
    street = models.CharField(max_length=50, verbose_name="Work Street", blank=True)
    zip_code = models.CharField(max_length=50, verbose_name="Work City", blank=True)
    city = models.CharField(max_length=50, verbose_name="Work Zip Code", blank=True)
    country = models.CharField(max_length=50, verbose_name="Work Country", blank=True)
    company_name = models.CharField(max_length=50, verbose_name="Company Name", blank=True)

    def __str__(self):
        return "{}".format(self.user.first_name)

    class Meta:
        verbose_name = "Employee Detail"
        verbose_name_plural = "Employee Details"


class QuestionDB(models.Model):
    CHOICE = [("Rating", "Rating"), ("ShortTextField", "ShortTextField"), ("LongTextField", "LongTextField")]
    question = models.TextField()
    answer_type = models.CharField(max_length=15, choices=CHOICE)

    class Meta:
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Bank"


class Survey(models.Model):
    name = models.CharField(max_length=50, verbose_name="Survey Name")
    employee_group = CountryField(blank_label="Employee Group", blank=True, null=True)
    question = models.ManyToManyField(QuestionDB, related_name="Question", blank=True)
