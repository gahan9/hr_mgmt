from django.contrib.auth import get_user_model
from rest_framework import serializers

from employee.models import Employee, QuestionDB
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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionDB
        fields = ['url', 'id', 'question']
