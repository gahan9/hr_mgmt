from main.models import *


class AccessLevel(models.Model):
    ACCESS_LEVEL = [("head_hr", "Head HR"), ("hr", "HR"), ("company", "Employee")]
    name = models.CharField(max_length=30, default="company", choices=ACCESS_LEVEL)


class Employee(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="company")
    company_name = models.ForeignKey(Company)
    registration_date = models.DateTimeField(auto_now=True)
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True, verbose_name="Alternate Contact Number")
    job_title = models.CharField(max_length=30, verbose_name="Job Title", blank=True)
    street = models.CharField(max_length=50, verbose_name="Work Street", blank=True)
    zip_code = models.CharField(max_length=50, verbose_name="Work Zip Code", blank=True)
    city = models.CharField(max_length=50, verbose_name="Work City", blank=True)
    country = models.CharField(max_length=50, verbose_name="Work Country", blank=True)

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

