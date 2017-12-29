import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from pyparsing import basestring
from requests.compat import basestring
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from main.models import Company, Plan, UserModel

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    has_plan = PrimaryKeyRelatedField(queryset=Plan.objects.all())
    password = serializers.CharField(max_length=32, style={'input_type': 'password'})
    profile_image = Base64ImageField(required=False)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data["password"])
        return super(UserSerializer, self).create(validated_data)

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
