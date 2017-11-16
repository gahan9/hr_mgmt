from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django_countries import countries
from django_countries.fields import LazyTypedMultipleChoiceField
from django_countries.widgets import CountrySelectWidget

from forms.helpers import file_upload_helper, survey_helper, create_staff_helper
from main.models import *


class LoginForm(AuthenticationForm):
    """Form to allow user to log in to system"""
    username = forms.CharField(label="Email", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'data-rule': 'email',
                                          'id': 'email', 'name': 'email',
                                          'style': 'background:rgba(227, 231, 228, 1)',
                                          'placeholder': 'Email'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'name': 'password', 'id': 'password',
                                          'style': 'background:rgba(227, 231, 228, 1)',
                                          'type': 'password', 'placeholder': 'Password'}))


class CreateStaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    alternate_email = forms.EmailField(widget=forms.EmailInput)
    job_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_no = forms.CharField(widget=forms.NumberInput)

    def __init__(self, *args, **kwargs):
        super(CreateStaffUserForm, self).__init__(*args, **kwargs)
        self.helper = create_staff_helper
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['job_title'].required = True
        self.fields['company_name'].required = True
        self.fields['alternate_email'].required = False

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'is_staff', 'first_name', 'last_name']


class FileUploadForm(forms.ModelForm):
    """Upload files with this form"""
    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.helper = file_upload_helper

    class Meta:
        model = FileUpload
        fields = "__all__"


class SurveyCreator1(forms.Form):
    name = forms.CharField(label="Survey Name", max_length=30,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Survey Name"})
                           )

    class Meta:
        model = Survey
        fields = ['name', ]


class SurveyCreator2(forms.Form):
    employee_group = LazyTypedMultipleChoiceField(choices=countries)

    class Meta:
        model = Survey
        fields = ['employee_group']
        widgets = {'employee_group': CountrySelectWidget()}
