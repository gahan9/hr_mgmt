import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from pyparsing import basestring
from requests.compat import basestring
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from main.models import Company, Plan, UserModel
from main.utility import computeMD5hash

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
    password = serializers.CharField(max_length=190, style={'input_type': 'password'}, required=False)
    profile_image = Base64ImageField(required=False)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data["password"])
        return super(UserSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        validated_data['password'] = make_password(computeMD5hash(validated_data["password"]))
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ['url', 'id', 'contact_number', 'first_name', 'last_name', 'gender', 'profile_image', 'email',
                  'password', 'role', 'registration_date', 'has_plan']
        read_only_fields = ('role', 'has_plan')
        # extra_kwargs = {'password': {'write_only': True}}
        write_only_fields = ('password', )


class CompanySerializer(serializers.ModelSerializer):
    """ Company Serializer """
    class Meta:
        model = Company
        fields = ["url", "id", "name", "alternate_contact_no", "alternate_email", "country", "company_user", ]
