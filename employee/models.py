import ast
from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from main.models import *


def default_start_time():
    return datetime.now()


def default_end_time():
    return default_start_time() + timedelta(days=7)


class Employee(models.Model):
    """
    Extends custom user model for login details and store other necessary details of employee
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="employee", on_delete=models.CASCADE)
    company_name = models.ForeignKey(Company, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now=True)
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True, verbose_name="Alternate Contact Number")
    job_title = models.CharField(max_length=30, verbose_name="Job Title", blank=True)
    street = models.CharField(max_length=50, verbose_name="Work Street", blank=True)
    zip_code = models.CharField(max_length=50, verbose_name="Work Zip Code", blank=True)
    city = models.CharField(max_length=50, verbose_name="Work City", blank=True)
    country = models.CharField(max_length=50, verbose_name="Work Country", blank=True)
    category = models.CharField(max_length=30, verbose_name="Category/Region", blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_by", blank=True, null=True)

    def __unicode__(self):
        return self.user.contact_number

    def __str__(self):
        return self.user.contact_number

    class Meta:
        verbose_name = "Employee Detail"
        verbose_name_plural = "Employee Details"


class QuestionDB(models.Model):
    """
    Question database - stores all the question added from any company
    """
    CHOICE = ((0, "MCQ"),  # content_type:
              (1, "Rating"),  # content_type:
              (2, "TextField"))  # content_type:
    question = models.TextField()
    answer_type = models.IntegerField(choices=CHOICE, default=1)
    benchmark = models.BooleanField(default=False)  # if True will be visible to every company
    asked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="is_asked_by", blank=True)
    created_on = models.DateTimeField(auto_now=True)
    # options to hold rate_value
    options = models.CharField(max_length=2, default=10, verbose_name="Rate Scale", help_text="Enter maximum value of rate scale up to 10")
    # discontinued generic relation for temporary basis
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField(blank=True, null=True)
    # content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.question

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Question Bank"


class MCQAnswer(models.Model):
    """
    MCQAnswer type in generic relationship with question
    """
    type = GenericRelation(QuestionDB)
    option = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.option

    def get_option_list(self):
        return ast.literal_eval(self.option)


class RatingAnswer(models.Model):
    """
    Rating answer type in generic relationship with question
    """
    type = GenericRelation(QuestionDB)
    rate_value = models.SmallIntegerField(blank=True, null=True, default=10)  # max_rating_value


class TextAnswer(models.Model):
    """
    Text answer type in generic relationship with question
    """
    type = GenericRelation(QuestionDB)
    text = models.TextField(blank=True, null=True)


class Survey(models.Model):
    """
    Survey model, stores survey details
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="survey_owner")
    name = models.CharField(max_length=50, verbose_name="Survey Name")
    employee_group = models.CharField(max_length=70, verbose_name="Region", blank=True, null=True)
    question = models.ManyToManyField(QuestionDB, blank=True, related_name="rel_question")
    steps = models.SmallIntegerField(default=1, verbose_name="Progress")
    complete = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=default_start_time, blank=True, null=True)
    end_date = models.DateTimeField(default=default_end_time, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def next_step(self):
        return self.steps + 1

    def get_question(self):
        return [p.question for p in self.question.all()]

    @property
    def total_question(self):
        return len(self.get_question())

    def __str__(self):
        return "{1}- {0}".format(self.name, self.id)


class SurveyResponse(models.Model):
    related_survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="rel_survey", verbose_name="related_survey_id")
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rel_employee", verbose_name="related_user_id")
    answers = models.TextField()
    complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
