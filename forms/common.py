from django.contrib.auth.forms import AuthenticationForm
from django import forms


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
