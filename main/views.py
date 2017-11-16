import os
import csv
import codecs
from datetime import datetime

from braces.views._access import SuperuserRequiredMixin
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
import django_tables2 as tables
from django_tables2.tables import Table
from django_tables2.views import MultiTableMixin, SingleTableView
from formtools.wizard.views import WizardView, SessionWizardView

from forms.common import *
from .models import *
from .tables import *
from employee_management.settings import BASE_DIR


class HomePageView(LoginRequiredMixin, TemplateView):
    # login_url = reverse_lazy('admin:index')
    login_url = reverse_lazy('login')
    template_name = "home.html"
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


class EmployeeDataView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = "employee_data.html"


class FieldRateView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = "field_rate.html"


class FileUploadView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = FileUploadForm
    success_url = reverse_lazy('file_upload')
    template_name = "file_upload.html"

    def server_dump_setup(self):
        # setup directory for error handling
        dump_dir = os.path.join(BASE_DIR, "server_dump")
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H:%M:%S")
        file_name = "failure_{}.csv".format(timestamp)
        file_location = os.path.join(dump_dir, file_name)
        return file_location, file_name

    def post(self, request, *args, **kwargs):
        user_file = self.request.FILES['file']
        count = 0
        no_of_user = 0
        failed_user = 0
        fieldnames = ['first_name', 'last_name', "mobile", "email", 'alternate_email', 'alternate_contact_no',
                      'job_title', 'street', 'zip_code', 'city', 'country', "error_reason"]
        try:
            csv_read = csv.DictReader(codecs.iterdecode(user_file, 'utf-8'))
            failure_store_location, file_name = self.server_dump_setup()
            for row in csv_read:
                password = row['first_name'] + "@" + row['mobile']
                try:
                    user_obj = User.objects.create(
                        username=row['mobile'],
                        password=make_password(password),
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )
                    EmployeeData.objects.create(user=user_obj, contact_no=row['mobile'],
                                                alternate_contact_no=row['alternate_contact_no'],
                                                alternate_email=row['alternate_email'],
                                                job_title=row['job_title'], street=row['street'],
                                                zip_code=row['zip_code'], city=row['city'],
                                                country=row['country']
                                                )
                    no_of_user += 1
                except IntegrityError as duplicate_error:
                    csv_file = open(failure_store_location, 'a')
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    if failed_user == 0:
                        writer.writeheader()
                    count += 1
                    # print("duplicate_error-----> {}".format(duplicate_error))
                    row['error_reason'] = "Unable to add employee because User with the same email already exist"
                    writer.writerow(row)
                    csv_file.close()
                    failed_user += 1
                except Exception as unknown_exception:
                    csv_file = open(failure_store_location, 'a')
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    if failed_user == 0:
                        writer.writeheader()
                    count += 1
                    print("unknown_exception-----> {}".format(unknown_exception))
                    row['error_reason'] = unknown_exception
                    writer.writerow(row)
            if failed_user > 0:
                messages.error(request, "Error: {} user(s) failed to create from {}".format(failed_user, user_file))
                response = HttpResponse(open(failure_store_location, "rb"), content_type='text/csv')
                response['Content-Disposition'] = "attachment; filename={filename}".format(
                    filename=file_name
                )
                # response['Content-Length'] = open(failure_store_location, "rb").tell()
                return response
        except Exception as file_error:
            print("File-Error-----> {}".format(file_error))
            messages.error(request, "Error: Invalid file type or header : '{}' . Please upload valid csv file".format(user_file))
            return HttpResponseRedirect("")
        if no_of_user > 0:
            messages.success(request, "{} user(s) created successfully".format(no_of_user))
        return super(FileUploadView, self).post(request, *args, **kwargs)


class AddFormMixin(object, ):
    def define_form(self):
        def get_form_field_type(f):
            if f == "user__email":
                return forms.CharField(required=False, label="Email")
            elif f == "user__first_name":
                return forms.CharField(required=False, label="First Name")
            elif f == "user__last_name":
                return forms.CharField(required=False, label="Last Name")
            return forms.CharField(required=False)
        attrs = dict((f, get_form_field_type(f)) for f in self.get_form_fields())
        klass = type('DForm', (forms.Form,), attrs)
        return klass

    def get_queryset(self):
        form_class = self.define_form()
        if self.request.GET:
            self.form = form_class(self.request.GET)
        else:
            self.form = form_class()
        qs = super(AddFormMixin, self).get_queryset()

        if self.form.data and self.form.is_valid():
            q_objects = Q()
            for f in self.get_form_fields():
                if self.form.cleaned_data.get(f):
                    q_objects &= Q(**{f + '__icontains': self.form.cleaned_data[f]})
            qs = qs.filter(q_objects)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(AddFormMixin, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx


class EmployeeDataList(LoginRequiredMixin, AddFormMixin, SingleTableView):
    login_url = reverse_lazy('login')
    model = EmployeeData
    template_name = "table_show.html"
    table_class = EmployeeDataTable
    table_pagination = {'per_page': 15}

    def get_form_fields(self):
        return ['user__first_name', 'user__last_name', 'contact_no', 'user__email', 'job_title', 'street', 'city', 'country']


class SurveyManager(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'survey.html'
    queryset = Survey.objects.all()


class AddSurvey(LoginRequiredMixin, SuccessMessageMixin, SessionWizardView):
    login_url = reverse_lazy('login')
    template_name = 'add_survey.html'
    success_url = reverse_lazy('survey_manage')
    form_list = [SurveyCreator1, SurveyCreator2]

    def done(self, form_list, **kwargs):
        for form in form_list:
            pass
        return render_to_response('done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

    # def form_valid(self, form):
    #     print("here... {}".format(self.object))
    #     return super(AddSurvey, self).form_valid(form)


class CreateStaffUserView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = CreateStaffUserForm
    template_name = "create_staff_user.html"
    success_url = reverse_lazy('create_staff')

    def form_valid(self, form):
        form_data = form.cleaned_data
        hr = User.objects.create(username=form_data['username'], email=form_data['email'],
                                 password=make_password(form_data['password']), is_staff=True,
                                 first_name=form_data['first_name'], last_name=form_data['last_name'],
                                 )
        EmployeeData.objects.create(user=hr, company_name=form_data['company_name'],
                                    alternate_email=form_data['alternate_email'],
                                    contact_no=form_data['contact_no'],
                                    job_title=form_data['job_title'])
        messages.success(self.request, "HR with username {} created successfully.".format(hr.username))
        return HttpResponseRedirect(reverse_lazy('create_staff'))
