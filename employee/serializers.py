from rest_framework import serializers

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
    def to_internal_value(self, data):
        return ContentType.objects.get(model=data)

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if value.model_class() == MCQAnswer:
            serializer = MCQSerializer(value, context=self.context)
        elif value.model_class() == RatingAnswer:
            serializer = RatingSerializer(value, context=self.context)
        elif value.model_class() == TextAnswer:
            serializer = TextSerializer(value, context=self.context)
        else:
            raise Exception("Unexpected object")
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
    answer_type = serializers.ChoiceField(choices=QuestionDB.CHOICE, style={'base_template': 'select.html'})
    content_type = ContentObjectRelatedField(read_only=True, default=ContentType.objects.get_for_model(MCQAnswer))

    class Meta:
        model = QuestionDB
        fields = ["url", "id", "question", "answer_type", 'content_type', "asked_by"]
        read_only_fields = ('asked_by', )


class SurveySerializer(serializers.HyperlinkedModelSerializer):
    """
    Survey serializer
    Relation: field question: many to many field
    """
    question = QuestionSerializer(partial=True, allow_null=True, many=True)
    created_by = UserSerializer(read_only=True)

    def create(self, validated_data):
        """
        creates survey with name as necessary parameter
        :param validated_data: data received in API/form
        :return: survey_instance: instance of survey object
        """
        requested_by = self.context['request'].user
        validated_data['created_by'] = requested_by
        # print(validated_data)
        steps = 1
        steps = 2 if 'employee_group' in validated_data and validated_data['employee_group'] else steps
        steps = 3 if steps == 2 and validated_data['question'] else steps
        if 'start_date' in validated_data and 'end_date' in validated_data:
            steps = 4 if steps == 3 and validated_data['start_date'] and validated_data['end_date'] else steps
        que_lis = validated_data.pop('question') if 'question' in validated_data else []
        existing_survey_instance = Survey.objects.filter(**validated_data)
        if existing_survey_instance:
            survey_instance = existing_survey_instance[0]
            # print("existing survey: {}".format(survey_instance))
        else:
            survey_instance = Survey(**validated_data, steps=steps)
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
        steps = 1
        steps = 2 if instance.employee_group else steps
        steps = 3 if steps == 2 and instance.question else steps
        steps = 4 if steps == 3 and instance.start_date and instance.end_date else steps
        instance.steps = steps
        return instance

    class Meta:
        model = Survey
        fields = ["url", "id", "name", "employee_group", "question", "steps", "complete",
                  "start_date", "end_date", "created_by"]
        read_only_fields = ('steps',)


class SurveyResponseSerializer(serializers.ModelSerializer):
    """ Serializer to take response of Survey """
    class Meta:
        model = SurveyResponse
        fields = ["url", "id", "related_survey", "related_user", "answers", "complete"]
