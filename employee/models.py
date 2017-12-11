from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from main.models import *


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
    CHOICE = ((0, "MCQ"),  # content_type: 16
              (1, "Rating"),  # content_type: 15
              (2, "TextField"))  # content_type: 14
    question = models.TextField()
    answer_type = models.IntegerField(choices=CHOICE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()
    asked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="is_asked_by", blank=True)
    created_on = models.DateTimeField(auto_now=True)

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


class RatingAnswer(models.Model):
    """
    Rating answer type in generic relationship with question
    """
    type = GenericRelation(QuestionDB)
    rate_value = models.SmallIntegerField(blank=True, null=True)


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
    employee_group = models.CharField(max_length=70, verbose_name="Employee Group|Country-Region", blank=True, null=True)
    question = models.ManyToManyField(QuestionDB, blank=True, related_name="rel_question")
    steps = models.SmallIntegerField(default=1)
    complete = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def next_step(self):
        return self.steps + 1

    def get_question(self):
        return [p.question for p in self.question.all()]

    def __str__(self):
        return "{1}- {0}".format(self.name, self.id)
