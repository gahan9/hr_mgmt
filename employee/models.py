from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from rest_framework.compat import MaxValueValidator, MinValueValidator

from main.models import *


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="employee", on_delete=models.CASCADE)
    company_name = models.ForeignKey(Company)
    registration_date = models.DateTimeField(auto_now=True)
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True, verbose_name="Alternate Contact Number")
    job_title = models.CharField(max_length=30, verbose_name="Job Title", blank=True)
    street = models.CharField(max_length=50, verbose_name="Work Street", blank=True)
    zip_code = models.CharField(max_length=50, verbose_name="Work Zip Code", blank=True)
    city = models.CharField(max_length=50, verbose_name="Work City", blank=True)
    country = models.CharField(max_length=50, verbose_name="Work Country", blank=True)
    category = models.CharField(max_length=30, verbose_name="Category/Region", blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_by", blank=True, null=True)

    def __unicode__(self):
        return self.user.contact_number

    class Meta:
        verbose_name = "Employee Detail"
        verbose_name_plural = "Employee Details"


class QuestionDB(models.Model):
    CHOICE = [("MCQ", "MCQ"), ("Rating", "Rating"), ("TextField", "TextField")]
    question = models.TextField()
    answer_type = models.CharField(max_length=15, choices=CHOICE)
    asked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="is_asked_by", blank=True)
    created_on = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = "Question Bank"
        verbose_name_plural = "Question Bank"


class MCQAnswer(models.Model):
    type = GenericRelation(QuestionDB)
    option = models.CharField(max_length=150, blank=True, null=True)


class RatingAnswer(models.Model):
    type = GenericRelation(QuestionDB)
    rate_value = models.SmallIntegerField(blank=True, null=True)


class TextAnswer(models.Model):
    type = GenericRelation(QuestionDB)
    text = models.TextField(blank=True, null=True)


class Survey(models.Model):
    name = models.CharField(max_length=50, verbose_name="Survey Name")
    employee_group = models.CharField(max_length=70, verbose_name="Employee Group|Country-Region", blank=True, null=True)
    question = GenericRelation(QuestionDB)
    steps = models.SmallIntegerField(default=0)
    complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
