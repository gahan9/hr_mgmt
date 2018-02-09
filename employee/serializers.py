import json
import time
from calendar import timegm

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from employee.models import *
from main.serializers import UserSerializer, CompanySerializer

User = get_user_model()


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Employee model serializer
    """
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
    def to_internal_value(self, content_type_key):
        """

        :param content_type_key: key of related content type
        :return:
        """
        return ContentType.objects.get(pk=content_type_key)

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, MCQAnswer):
            serializer = MCQSerializer(value, context=self.context)
        elif isinstance(value, RatingAnswer):
            serializer = RatingSerializer(value, context=self.context)
        elif isinstance(value, TextAnswer):
            serializer = TextSerializer(value, context=self.context)
        else:
            # print(value)
            try:
                # print(value.model)
                return value.serializable_value
            except Exception as e:
                print(e)
                raise Exception("Unexpected object: {}".format(value))
        return serializer.data


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
    # answer_type = serializers.ChoiceField(choices=QuestionDB.CHOICE, style={'base_template': 'select.html'})
    # content_object = ContentObjectRelatedField(queryset=ContentType.objects.all(), required=False)
    # option = serializers.SerializerMethodField()
    question_id = serializers.SerializerMethodField(required=False, read_only=True)
    question_title = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = QuestionDB
        fields = ["url", "question_id", "question", "question_title", "answer_type", 'options', "asked_by"]
        read_only_fields = ('asked_by', 'content_object')

    def get_question_id(self, obj):
        return obj.id

    def get_question_title(self, obj):
        return obj.question

    def get_option(self, obj):
        print("in get option........... ", self, obj)
        return []
        # possible_fields = ['options', 'rate_value', 'text']
        # choice_object = obj.content_object.objevct.get(id=obj.object_id)
        # return choice_object._meta.fields if choice_object.name in possible_fields else getattr(choice_object, choice_object.name)


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Survey serializer
    Relation: field question: many to many field
    """
    employee_group = serializers.CharField(
        max_length=100,
        style={'placeholder': 'Select Employee Group', 'hide_label': True,
               # 'autofocus': True
               }, required=False)
    start_date = serializers.DateTimeField(
        style={'placeholder': 'Select start date',
               # 'autofocus': True
               }, required=False)
    end_date = serializers.DateTimeField(style={
        'id': 'survey-end-date', 'placeholder': 'Select End date'}, required=False)
    complete = serializers.BooleanField(style={
        'placeholder': 'Completed??'}, required=False)
    question = QuestionSerializer(partial=True, allow_null=True, many=True, required=False)
    created_by = UserSerializer(read_only=True)
    current_time = serializers.SerializerMethodField(read_only=True)
    total_question = serializers.SerializerMethodField(read_only=True)
    responded = serializers.SerializerMethodField(required=False)
    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)

    def get_responded(self, obj):
        """ Get if user has already responded for this survey object or not """
        current_user = self.context['request'].user
        responded_survey_list = SurveyResponse.objects.filter(related_user=current_user, related_survey=obj)
        # print(current_user, responded_survey_list)
        if responded_survey_list:
            return responded_survey_list[0].complete
        else:
            return False

    def get_start_time(self, obj):
        return timegm(obj.start_date.utctimetuple())

    def get_end_time(self, obj):
        return timegm(obj.end_date.utctimetuple())

    def get_current_time(self, obj):
        return time.time()

    def get_total_question(self, obj):
        return len(obj.question.all())

    def create(self, validated_data):
        """
        creates survey with name as necessary parameter
        :param validated_data: data received in API/form
        :return: survey_instance: instance of survey object
        """
        requested_by = self.context['request'].user
        validated_data['created_by'] = requested_by
        # print(validated_data)
        # steps = 1
        # steps = 2 if 'employee_group' in validated_data and validated_data['employee_group'] else 1
        # steps = 3 if 'question' in validated_data and validated_data['question'] else 2
        # if 'start_date' in validated_data and 'end_date' in validated_data:
        #     steps = 4 if validated_data['start_date'] and validated_data['end_date'] else 3
        que_lis = validated_data.pop('question') if 'question' in validated_data else []
        existing_survey_instance = Survey.objects.filter(**validated_data)
        if existing_survey_instance:
            survey_instance = existing_survey_instance[0]
            # print("existing survey: {}".format(survey_instance))
        else:
            survey_instance = Survey(**validated_data)
            survey_instance.save()
        # print(que_lis)
        for item in que_lis:
            item.pop('asked_by') if 'asked_by' in item else []
            if item['answer_type'] == 0:
                existing_question = QuestionDB.objects.filter(**item, asked_by=requested_by)
            else:
                existing_question = QuestionDB.objects.filter(**item)
            if existing_question:
                question_instance = existing_question[0]
            else:
                question_instance = QuestionDB(**item)
                question_instance.save()
            question_instance.asked_by.add(requested_by)
            survey_instance.question.add(question_instance)
        return survey_instance

    def update(self, instance, validated_data):
        """
        update value of existing survey instance
        :param instance: survey instance
        :param validated_data: details
        :return:
        """
        for attr, value in validated_data.items():
            if not attr == "question":
                setattr(instance, attr, value)
        instance.save()
        # steps = 1
        # steps = 2 if instance.employee_group else steps
        # steps = 3 if steps == 2 and instance.question else steps
        # steps = 4 if steps == 3 and instance.start_date and instance.end_date else steps
        # instance.steps = steps
        return instance

    class Meta:
        model = Survey
        fields = ["url", "id", "name", "responded", "employee_group", "question", "steps", "complete",
                  "start_date", "end_date", "created_by",
                  "start_time", "end_time",
                  "current_time", "total_question",
                  ]


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class SurveyResponseSerializer(serializers.ModelSerializer):
    """ Serializer to take response of Survey """
    answers = serializers.JSONField()
    survey_id = serializers.PrimaryKeyRelatedField(source='related_survey', queryset=Survey.objects.filter(complete=True))

    def validate(self, attrs):
        attrs['related_user'] = self.context['request'].user
        # this block is to store values in database in desire format
        answers = attrs['answers']
        result = {
            str(question_response.pop("q")): question_response
            for question_response in answers if "q" in question_response}
        print(result)
        attrs['answers'] = result
        print(attrs)
        return attrs

    def create(self, validated_data):
        instance = super(SurveyResponseSerializer, self).create(validated_data)
        instance.related_user = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = SurveyResponse
        fields = ["url", "id", "survey_id", "related_user", "answers", "complete"]
        read_only_fields = ('related_user', )


class NewsFeedSerializer(serializers.ModelSerializer):
    date_created_epoch = serializers.SerializerMethodField()
    date_updated_epoch = serializers.SerializerMethodField()

    def validate(self, attrs):
        attrs['created_by'] = self.context['request'].user
        return attrs

    def get_date_created_epoch(self, obj):
        return timegm(obj.date_created.utctimetuple())

    def get_date_updated_epoch(self, obj):
        return timegm(obj.date_updated.utctimetuple())

    class Meta:
        model = NewsFeed
        fields = ["url", "id", "title", "feed", "priority", "created_by", "date_created", "date_updated",
                  "date_created_epoch", "date_updated_epoch"]
        read_only_fields = ('created_by', 'priority')
