from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django_countries import countries
from django_countries.fields import LazyTypedMultipleChoiceField
from django_countries.widgets import CountrySelectWidget

from forms.helpers import *
from main.models import *
from employee.models import *


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


class CreateCompanyForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    alternate_email = forms.EmailField(widget=forms.EmailInput)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    alternate_contact_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CreateCompanyForm, self).__init__(*args, **kwargs)
        self.helper = create_company_helper
        self.fields['email'].required = True
        self.fields['alternate_email'].required = True
        self.fields['alternate_contact_no'].required = False

    class Meta:
        model = UserModel
        fields = ['contact_number', 'first_name', 'last_name', 'password', 'email', 'is_head_hr', 'is_hr']


class CreateStaffUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    alternate_email = forms.EmailField(widget=forms.EmailInput)
    job_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    alternate_contact_no = forms.CharField(widget=forms.NumberInput)

    def __init__(self, *args, **kwargs):

        super(CreateStaffUserForm, self).__init__(*args, **kwargs)
        self.helper = create_hr_helper
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['job_title'].required = True
        self.fields['alternate_email'].required = False
        self.fields['alternate_contact_no'].required = False

    class Meta:
        model = UserModel
        fields = ['contact_number', 'first_name', 'last_name', 'password', 'email', 'is_head_hr', 'is_hr']


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
