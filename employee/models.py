import ast
import time
from calendar import timegm
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Count, F
from django.utils.translation import ugettext_lazy as _

from main.models import *
from .utils import CustomJSONField as JSONField


def default_start_time():
    return timezone.now()


def default_end_time():
    return default_start_time() + timedelta(days=7)


class Employee(models.Model):
    """
    Extends custom user model for login details and store other necessary details of employee
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="employee", on_delete=models.CASCADE)
    company_name = models.ForeignKey(Company, on_delete=models.CASCADE)
    alternate_email = models.EmailField(_("Alternate Email"), blank=True, null=True)
    alternate_contact_no = models.CharField(_("Alternate Contact Number"), max_length=15, blank=True, null=True)
    job_title = models.CharField(_("Job Title"), max_length=30, blank=True)
    street = models.CharField(_("Work Street"), max_length=50, blank=True)
    zip_code = models.CharField(_("Work Zip Code"), max_length=50, blank=True)
    city = models.CharField(_("Work City"), max_length=50, blank=True)
    country = models.CharField(_("Work Country"), max_length=50, blank=True)
    category = models.CharField(_("Category/Region"), max_length=30, blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_by", blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    @property
    def has_alternate_email(self):
        return bool(self.alternate_email)

    @property
    def has_alternate_contact_no(self):
        return bool(self.alternate_contact_no)

    def __unicode__(self):
        return self.user.contact_number

    def __str__(self):
        return str(self.user.contact_number)

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
    options = models.IntegerField(default=10, verbose_name="Rate Scale",
                                  help_text="Enter maximum value of rate scale up to 10",
                                  validators=[MaxValueValidator(10), MinValueValidator(1)]
                                  )
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
    name = models.CharField(_("Survey Name"), max_length=50)
    employee_group = models.CharField(_("Region"), max_length=70, blank=True, null=True)
    question = models.ManyToManyField(QuestionDB, blank=True, related_name="rel_question")
    steps = models.SmallIntegerField(_("Progress"), default=1)
    complete = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=default_start_time, blank=True, null=True)
    end_date = models.DateTimeField(default=default_end_time, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @property
    def next_step(self):
        return self.steps + 1

    @property
    def start_time(self):
        return timegm(self.start_date.utctimetuple())

    @property
    def end_time(self):
        return timegm(self.end_date.utctimetuple())

    @property
    def is_active(self):
        return bool(self.start_time <= time.time() <= self.end_time)

    @property
    def get_response(self):
        return SurveyResponse.objects.filter(related_survey=self).annotate(city=F('related_user__employee__city')).order_by('related_user__employee__city')

    @property
    def get_flat_answers(self):
        return self.get_response.values_list('answers', 'related_user__employee__city')

    @property
    def get_city_response_count(self):
        return self.get_response.annotate(city=F('related_user__employee__city')).values('city').annotate(responses=Count('city')).order_by('city')

    @property
    def get_responded_city(self):
        return self.get_response.values_list('related_user__employee__city', flat=True).distinct()

    def filter_score_response(self, city=None):
        """

        :param city: optional parameter, filters result for city if argument passed
        :return: dictionary
        {
        '<question-id>' : {
            'rates': {'<passed-rating>': <count-of-rating>, ....}
            'rating': <total-rating>
            'total_responses': <total-responses>
            }
        }
        """
        _answers = [i for i in self.get_flat_answers if i[1].lower() == city.lower()] if city else self.get_flat_answers
        _temp_dict = {}
        for _response, _city in _answers:
            for _question in _response:
                _rating = _response[_question]['r']
                comment = _response[_question]['m']
                _temp_dict[_question]['rating'] = _temp_dict.setdefault(_question, {}).setdefault('rating', 0) + _rating
                _temp_dict[_question]['total_responses'] = _temp_dict.setdefault(_question, {}).setdefault('total_responses', 1)
                _temp_dict[_question]['rates'][_rating] = _temp_dict[_question].setdefault('rates', {}).setdefault(_rating, 1) + 1
                if comment:
                    _temp_dict[_question].setdefault('comments', []).append(comment)
        return _temp_dict

    def filter_benchmark(self, city=None):
        _raw_dict = self.filter_score_response(city)
        _response_dict = {}
        for i, j in _raw_dict.items():
            question_instance = QuestionDB.objects.get(id=int(i))
            j.update({
                'average_rating': j['rating'] / j['total_responses'],
                'question_title': question_instance.question,
                'rate_scale': question_instance.options,
                'cities': self.get_responded_city,
                'city_response': self.get_city_response_count
            })
            _response_dict[int(i)] = j
        _response_dict['count'] = len(_response_dict)
        return _response_dict

    @property
    def score_response(self):
        return self.filter_score_response()

    @property
    def benchmark(self):
        return self.filter_benchmark()

    @property
    def get_question(self):
        return [p.question for p in self.question.all()]

    @property
    def total_question(self):
        return len(self.question.all())

    def __str__(self):
        return "{1}- {0}".format(self.name, self.id)


class SurveyResponse(models.Model):
    related_survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_("related_survey_id"),
                                       related_name="rel_survey")
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("related_user_id"),
                                     related_name="rel_employee", blank=True, null=True)
    answers = JSONField()
    complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @property
    def get_city(self):
        if hasattr(self.related_user, "employee"):
            return self.related_user.employee.city
        else:
            return ""

    def __str__(self):
        return "{} - {}".format(self.related_survey, self.answers)

    class Meta:
        verbose_name_plural = "Survey Response"


class FileUpload(models.Model):
    """ File Upload Model """
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(_("File"), upload_to='.')
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.file)

    class Meta:
        verbose_name_plural = "Uploads"


class NewsFeed(models.Model):
    """ News Feed model to broadcast message to all employee """
    title = models.CharField(max_length=50)
    feed = models.TextField()
    priority = models.IntegerField(blank=True, null=True, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "News Feed"


class GeoLocations(models.Model):
    address = models.CharField(_("City or address"), max_length=254, unique=True)
    lat = models.FloatField(_("Latitude"), null=True, blank=True)
    lng = models.FloatField(_("Longitude"), null=True, blank=True)

    @property
    def has_geolocation(self):
        return bool(self.lat and self.lng)

    @property
    def get_lat_long(self):
        lat_lng = {}
        if self.has_geolocation:
            lat_lng.update({'lat' : self.lat, 'long': self.lng})
        return lat_lng
