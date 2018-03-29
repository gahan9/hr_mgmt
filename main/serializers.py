import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from requests.compat import basestring
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from main.models import Company, Plan, UserModel
from main.utility import *

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension
            with open('file.txt', 'w') as f:
                f.write(data)
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'url', 'get_plan_name_display', 'get_price', 'plan_validity']


class UserSerializer(serializers.ModelSerializer):
    """ User serializer """
    has_plan = PrimaryKeyRelatedField(queryset=Plan.objects.all())
    contact_number = serializers.IntegerField(
        style={'placeholder': 'Contact Number', 'hide_label': True})
    first_name = serializers.CharField(
        style={'placeholder': 'First Name', 'hide_label': True})
    last_name = serializers.CharField(
        style={'placeholder': 'Last Name', 'hide_label': True})
    email = serializers.CharField(
        style={'placeholder': 'Email Address', 'hide_label': True})
    gender = serializers.ChoiceField(
        choices=UserModel.GENDER_CHOICE,
        style={'placeholder': 'Select Gender', 'hide_label': True})
    password = serializers.CharField(
        max_length=190,
        style={'input_type': 'password', 'placeholder': 'Password', 'hide_label': True})
    profile_image = Base64ImageField(
        required=False,
        style={'class': 'form-control clearablefileinput', 'placeholder': 'Profile Image'})

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = set_password_hash(validated_data["password"])
        return super(UserSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        validated_data['password'] = set_password_hash(validated_data["password"])
        return super(UserSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ['url', 'id', 'contact_number', 'first_name', 'last_name', 'gender', 'profile_image', 'email',
                  'password', 'role', 'registration_date', 'has_plan']
        read_only_fields = ['has_plan']
        write_only_fields = ('password', )


class CompanySerializer(serializers.ModelSerializer):
    """ Company Serializer """
    class Meta:
        model = Company
        fields = ["url", "id", "name", "alternate_contact_no", "alternate_email", "country", "company_user", ]
