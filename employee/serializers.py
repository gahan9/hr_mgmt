from django.contrib.auth import get_user_model
from rest_framework import serializers

from employee.models import *
from main.serializers import UserSerializer, CompanySerializer

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    added_by = UserSerializer()
    company_name = CompanySerializer()

    class Meta:
        model = Employee
        fields = ['url', 'id', 'user', 'company_name',
                  'alternate_contact_no', 'alternate_email',
                  'job_title', 'street', 'zip_code', 'city', 'country',
                  'added_by', 'registration_date'
                  ]


class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, MCQAnswer):
            return 'MCQ: {}'.format(value.option)
        elif isinstance(value, RatingAnswer):
            return 'Rate: {}'.format(value.rate_value)
        elif isinstance(value, TextAnswer):
            return 'Text: ' + value.text
        elif isinstance(value, QuestionDB):
            return QuestionSerializer(value)
        raise Exception('Unexpected type of tagged object')


class MCQSerializer(serializers.ModelSerializer):
    # answer_type = ContentObjectRelatedField(many=True, queryset=MCQAnswer.objects.all())

    class Meta:
        model = MCQAnswer
        fields = ['url', 'id', 'option']


class RatingSerializer(serializers.ModelSerializer):
    # answer_type = ContentObjectRelatedField(many=True, queryset=RatingAnswer.objects.all())

    class Meta:
        model = RatingAnswer
        fields = ['url', 'id', 'rate_value']


class TextSerializer(serializers.ModelSerializer):
    # answer_type = ContentObjectRelatedField(many=True, queryset=TextAnswer.objects.all())

    class Meta:
        model = TextAnswer
        fields = ['url', 'id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    # content_type = ContentObjectRelatedField(queryset=QuestionDB.objects.all())

    class Meta:
        model = QuestionDB
        fields = ["url", "id", "question", "answer_type", 'content_type', "asked_by"]
        # read_only_fields = ('content_type', 'object_id', 'content_object')


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    # question = QuestionSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = ["url", "id", "name", "employee_group", "steps", "complete"]
