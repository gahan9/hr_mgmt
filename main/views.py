import codecs
import csv
import os
from datetime import datetime

from braces.views._access import SuperuserRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django_tables2.views import SingleTableView
from formtools.wizard.views import SessionWizardView
from rest_framework import viewsets

from employee.tables import *
from employee_management.settings import BASE_DIR
from forms.common import *
from main.serializers import *

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('employee__company_name', 'role')


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class CreateCompanyView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    template_name = "field_rate/create_company.html"
    form_class = CreateCompanyForm
    success_url = reverse_lazy('create_company')

    def form_valid(self, form):
        form_data = form.cleaned_data
        hr = UserModel.objects.create(contact_number=form_data['contact_number'], email=form_data['email'],
                                      first_name=form_data['first_name'], last_name=form_data['last_name'],
                                      password=make_password(form_data['password']),
                                      is_hr=form_data['role'],
                                      )
        company_obj = Company.objects.create(company_user=hr, name=form_data['name'],
                                             alternate_contact_no=form_data['alternate_contact_no'],
                                             alternate_email=form_data['alternate_email'],
                                             country=form_data['country'])
        messages.success(self.request, "HR {} with contact_number {} created successfully.".format(hr.first_name, hr.contact_number))
        return HttpResponseRedirect(reverse_lazy('create_company'))
        # return super(CreateCompanyView, self).form_valid(form)
