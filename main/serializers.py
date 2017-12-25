from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from main.models import Company, Plan

User = get_user_model()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    has_plan = PrimaryKeyRelatedField(queryset=Plan.objects.all())
    password = serializers.CharField(max_length=32, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['url', 'contact_number', 'first_name', 'last_name', 'profile_image', 'email',
                  'password', 'role', 'registration_date', 'has_plan']
        # extra_kwargs = {'password': {'write_only': True}}


class CompanySerializer(serializers.ModelSerializer):
    """ Company Serializer """
    class Meta:
        model = Company
        fields = ["url", "id", "name", "alternate_contact_no", "alternate_email", "country", "company_user", ]
