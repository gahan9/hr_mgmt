from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.forms.models import ModelForm
from django_countries import countries
from django_countries.fields import LazyTypedMultipleChoiceField
from django_countries.widgets import CountrySelectWidget

from forms.helpers import *
from main.models import *
from employee.models import *
from main.utility import computeMD5hash


class LoginForm(AuthenticationForm):
    """Form to allow user to log in to system"""
    username = forms.CharField(label="Contact Number", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'type': 'text',
                                          'aria-describedby': "emailHelp",
                                          'id': 'email', 'name': 'email',
                                          'placeholder': 'Enter Contact Number'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'name': 'password', 'id': 'password',
                                          'type': 'password', 'placeholder': 'Password'}))

    def clean(self):
        if 'password' in self.cleaned_data:
            password = computeMD5hash(self.cleaned_data.get('password'))
            self.cleaned_data['password'] = password
        return super(LoginForm, self).clean()


class CreateCompanyForm(forms.ModelForm):
    """ Create Company """
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

    def clean(self):
        if 'password' in self.cleaned_data:
            password = computeMD5hash(self.cleaned_data.get('password'))
            self.cleaned_data['password'] = password
        return super(CreateCompanyForm, self).clean()

    class Meta:
        model = UserModel
        fields = ['contact_number', 'first_name', 'last_name', 'profile_image', 'password', 'email', 'role']


class CreateUserForm(forms.ModelForm):
    """ Create user """
    password = forms.CharField(widget=forms.PasswordInput)
    alternate_email = forms.EmailField(widget=forms.EmailInput)
    job_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    alternate_contact_no = forms.CharField(widget=forms.NumberInput)
    profile_image = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.helper = create_user_helper
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['job_title'].required = True
        self.fields['alternate_email'].required = False
        self.fields['alternate_contact_no'].required = False
        self.fields['profile_image'].required = False

    def clean(self):
        if 'password' in self.cleaned_data:
            password = computeMD5hash(self.cleaned_data.get('password'))
            self.cleaned_data['password'] = password
        return super(CreateUserForm, self).clean()

    class Meta:
        model = UserModel
        fields = ['contact_number', 'first_name', 'last_name', 'profile_image', 'password', 'email', 'role']


class EditUserForm(ModelForm):
    """ Edit employee data of form """
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.helper = edit_user_helper

    def clean(self):
        if 'password' in self.cleaned_data:
            password = computeMD5hash(self.cleaned_data.get('password'))
            self.cleaned_data['password'] = password
        return super(EditUserForm, self).clean()

    class Meta:
        model = UserModel
        fields = ['contact_number', 'first_name', 'last_name', 'profile_image', 'email', 'role']


class EditEmployeeForm(ModelForm):
    """ Edit associated employee profile data of user """
    def __init__(self, *args, **kwargs):
        super(EditEmployeeForm, self).__init__(*args, **kwargs)
        self.helper = edit_employee_data_helper

    class Meta:
        model = Employee
        fields = ['alternate_contact_no', 'alternate_email', 'job_title', 'street', 'zip_code', 'city', 'country']


class FileUploadForm(forms.ModelForm):
    """Upload files with this form"""
    category = forms.CharField(widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.helper = file_upload_helper

    class Meta:
        model = FileUpload
        fields = "__all__"
