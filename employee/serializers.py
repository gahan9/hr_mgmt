from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse

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
    def create(self, validated_data):
        existing_survey_instance = QuestionDB.objects.filter(**validated_data)
        if existing_survey_instance:
            return existing_survey_instance[0]
        else:
            return super(QuestionSerializer, self).create(validated_data)

    # def get_question_url(self, obj):
    #     survey_id = self.context.get('survey_id')
    #     url = reverse('api_customer_rep',
    #                   kwargs={'survey_id': survey_id,
    #                           'question_id': obj.id},
    #                   request=self.serializer.context.get('request'))
    #     return url

    class Meta:
        model = QuestionDB
        fields = ["url", "id", "question", "answer_type", 'content_type', "asked_by"]
        read_only_fields = ('asked_by', )


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(partial=True, allow_null=True, many=True)
    created_by = UserSerializer(read_only=True)
    # question = serializers.SerializerMethodField()
    # question = serializers.HyperlinkedRelatedField(QuestionDB.objects.all(), many=True, view_name='detail')

    # def get_question(self, obj):
    #     question = obj.question
    #     serializer_context = {'request': self.context.get('request'),
    #                           'survey_id': obj.id}
    #     serializer = QuestionSerializer(question, context=serializer_context)
    #     return serializer.data

    def create(self, validated_data):
        requested_by = self.context['request'].user
        validated_data['created_by'] = requested_by
        print(validated_data)
        que_lis = validated_data.pop('question') if 'question' in validated_data else []
        existing_survey_instance = Survey.objects.filter(**validated_data)
        steps = 1
        steps = 2 if validated_data['employee_group'] else steps
        steps = 3 if validated_data['employee_group'] and validated_data['question'] else steps
        if existing_survey_instance:
            survey_instance = existing_survey_instance[0]
            print("existing survey: {}".format(survey_instance))
        else:
            survey_instance = Survey(**validated_data)
            survey_instance.save()
        print(que_lis)
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

    class Meta:
        model = Survey
        fields = ["url", "id", "name", "employee_group", "question", "steps", "complete", "created_by"]
        read_only_fields = ('steps',)
