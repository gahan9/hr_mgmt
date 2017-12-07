from django.contrib.auth import get_user_model
from rest_framework import serializers

from main.models import Company

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    class Meta:
        model = User
        fields = ['url', 'contact_number', 'first_name', 'last_name', 'profile_image', 'email', 'password',
                  'role', 'registration_date']
        # extra_kwargs = {'password': {'write_only': True}}


class CompanySerializer(serializers.ModelSerializer):
    """ Company Serializer """
    class Meta:
        model = Company
        fields = ["url", "id", "name", "alternate_contact_no", "alternate_email", "country", "company_user", ]
