import codecs
import csv
import os
from datetime import datetime

from bootstrap3 import renderers
from django.contrib import messages
from django.contrib.auth import mixins
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django_tables2.views import SingleTableView
from formtools.wizard.views import SessionWizardView
from rest_framework import viewsets, generics, status
from rest_framework.decorators import detail_route
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response

from employee_management.settings import BASE_DIR
from employee.tables import *
from employee.serializers import *
from forms.common import *


def get_user_company(user):
    if hasattr(user, 'employee'):
        return user.employee.company_name
    elif hasattr(user, 'rel_company_user'):
        return user.rel_company_user


class HomePageView(LoginRequiredMixin, TemplateView):
    # login_url = reverse_lazy('admin:index')
    login_url = reverse_lazy('login')
    template_name = "company/home.html"
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['users'] = UserModel.objects.all()
        return context


class EmployeeDataView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = "company/employee_data.html"


class FieldRateView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = "company/field_rate.html"


class FileUploadView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('login')
    form_class = FileUploadForm
    success_url = reverse_lazy('file_upload')
    template_name = "company/file_upload.html"

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
        current_user = self.request.user
        current_user_company = get_user_company(current_user)
        print(current_user, current_user_company)
        user_file = self.request.FILES['file']
        count = 0
        no_of_user = 0
        failed_user = 0
        fieldnames = ['contact_number', 'first_name', 'last_name', 'email', 'alternate_email',
                      'alternate_contact_no', 'job_title', 'street', 'zip_code', 'city', 'country',
                      'role', 'password', 'error_reason']
        try:
            csv_read = csv.DictReader(codecs.iterdecode(user_file, 'utf-8'))
            failure_store_location, file_name = self.server_dump_setup()
            for row in csv_read:
                password_generated = row['first_name'] + "@" + row['contact_number']
                if "password" in row.keys():
                    password = row['password'] if row['password'] else password_generated
                else:
                    password = password_generated
                try:
                    user_obj = UserModel.objects.create(
                        contact_number=row['contact_number'],
                        password=make_password(password),
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        role=3  # employee
                    )
                    ActivityMonitor.objects.create(activity_type=0, company_id=current_user_company.id,
                                                   performed_by=current_user.get_detail(),
                                                   affected_user=user_obj.get_detail(), bulk_create=True)
                    Employee.objects.create(user=user_obj, company_name=current_user_company,
                                            alternate_contact_no=row['alternate_contact_no'],
                                            alternate_email=row['alternate_email'],
                                            job_title=row['job_title'],
                                            street=row['street'], zip_code=row['zip_code'], city=row['city'],
                                            country=row['country'], added_by=current_user
                                            )
                    no_of_user += 1
                    print("success...")
                except IntegrityError as duplicate_error:
                    csv_file = open(failure_store_location, 'a')
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    if failed_user == 0:
                        writer.writeheader()
                    count += 1
                    print("duplicate_error-----> {}".format(duplicate_error))
                    row[
                        'error_reason'] = "Unable to add company because User with the same email already exist more-detail:{}".format(
                        duplicate_error)
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
            messages.error(request,
                           "Error: Invalid file type or header : '{}' . Please upload valid csv file".format(user_file))
            # return HttpResponseRedirect("")
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
    model = Employee
    template_name = "company/employee_detail.html"
    table_class = EmployeeTable

    table_pagination = {'per_page': 15}

    def get_form_fields(self):
        return ['user__first_name', 'user__last_name', 'user__contact_number', 'user__email', 'job_title', 'street',
                'city', 'country']

    def get_queryset(self):
        current_user = self.request.user
        try:
            company_id = Company.objects.get(id=Employee.objects.get(user=current_user).company_name.id)
        except Exception as e:
            # if user in this exception means user itself a company-owner
            print(e)
            company_id = Company.objects.get(company_user=current_user)
        if self.queryset is None:
            self.queryset = Employee.objects.filter(company_name=company_id, user__role__gte=current_user.role)
        return super(EmployeeDataList, self).get_queryset()


class SurveyManager(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'company/survey.html'
    queryset = Survey.objects.all()


class AddSurvey(LoginRequiredMixin, SuccessMessageMixin, SessionWizardView):
    login_url = reverse_lazy('login')
    template_name = 'company/add_survey.html'
    success_url = reverse_lazy('survey_manage')

    form_list = [SurveyCreator1, SurveyCreator2]

    def done(self, form_list, **kwargs):
        for form in form_list:
            pass

        return render_to_response('common/done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })


class CreateUserView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    form_class = CreateUserForm
    template_name = "company/create_user.html"
    success_url = reverse_lazy('create_user')

    def form_valid(self, form):
        current_user = self.request.user
        current_user_company = Company.objects.get(company_user=current_user)
        form_data = form.cleaned_data
        set_role = 3 if form_data['role'] < current_user.role else form_data['role']
        user_obj = UserModel.objects.create(contact_number=form_data['contact_number'], email=form_data['email'],
                                            first_name=form_data['first_name'], last_name=form_data['last_name'],
                                            password=make_password(form_data['password']),
                                            role=set_role,
                                            )
        activity_obj = ActivityMonitor.objects.create(activity_type=0, performed_by=current_user.get_detail(),
                                                      company_id=current_user_company.id,
                                                      affected_user=user_obj.get_detail())
        Employee.objects.create(user=user_obj, company_name=current_user_company,
                                job_title=form_data['job_title'],
                                alternate_email=form_data['alternate_email'],
                                alternate_contact_no=form_data['alternate_contact_no'],
                                street=form_data['street'], zip_code=form_data['zip_code'],
                                city=form_data['city'], country=form_data['country']
                                )
        messages.success(self.request,
                         "HR {} {} created successfully.".format(user_obj.first_name, user_obj.last_name))
        return HttpResponseRedirect(reverse_lazy('create_user'))

    def form_invalid(self, form):
        msg = "Error: invalid data... {}".format(form.errors)
        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('create_user'))


class EditEmployeeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    template_name = 'company/edit_user.html'
    model = Employee
    success_url = reverse_lazy('view_data')
    form_class = EditEmployeeForm
    success_message = "Details updated successfully."

    def form_valid(self, form, **kwargs):
        user_object = Employee.objects.get(id=self.kwargs['pk']).user
        company_id = get_user_company(self.request.user).id
        ActivityMonitor.objects.create(activity_type=1, company_id=company_id,
                                       performed_by=self.request.user.get_detail(),
                                       affected_user=user_object.get_detail())
        return super(EditEmployeeView, self).form_valid(form)

    def form_invalid(self, form):
        user_object = Employee.objects.get(id=self.kwargs['pk']).user
        company_id = get_user_company(self.request.user).id
        ActivityMonitor.objects.create(activity_type=1, company_id=company_id, status=False,
                                       performed_by=self.request.user.get_detail(),
                                       affected_user=user_object.get_detail())
        return super(EditEmployeeView, self).form_invalid(form)


class EditUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    template_name = 'company/edit_user.html'
    model = UserModel
    success_url = reverse_lazy('view_data')
    form_class = EditUserForm
    success_message = "Details updated successfully."

    def form_valid(self, form, **kwargs):
        current_user = self.request.user
        user_object = UserModel.objects.get(id=self.kwargs['pk'])
        company_id = get_user_company(current_user).id
        activity_obj = ActivityMonitor.objects.create(activity_type=1,
                                                      company_id=company_id,
                                                      performed_by=self.request.user.get_detail(),
                                                      affected_user=user_object.get_detail())
        return super(EditUserView, self).form_valid(form)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = UserModel
    success_message = "'%(name)s'  deleted..."
    success_url = reverse_lazy("view_data")

    def delete(self, request, *args, **kwargs):
        current_user = self.request.user
        company_id = get_user_company(current_user).id
        user_object = self.get_object()
        value_user = [user_object.contact_number, user_object.first_name, user_object.last_name]
        del_msg = "{}".format(value_user)
        activity_obj = ActivityMonitor.objects.create(remarks=del_msg, activity_type=2,
                                                      company_id=company_id,
                                                      performed_by=self.request.user.get_detail(),
                                                      affected_user=user_object.get_detail())
        print(activity_obj)
        message = 'User: {} (M: {}) deleted successfully'.format(user_object.first_name, user_object.contact_number)
        messages.success(self.request, message)
        return super(EmployeeDeleteView, self).delete(request, *args, **kwargs)


class ActivityMonitorView(LoginRequiredMixin, SingleTableView):
    login_url = reverse_lazy('login')
    table_class = ActivityTable
    model = ActivityMonitor
    template_name = "company/employee_detail.html"
    table_pagination = {'per_page': 15}

    def get_queryset(self):
        current_user = self.request.user
        company_id = get_user_company(current_user).id
        if self.queryset is None:
            self.queryset = ActivityMonitor.objects.filter(company_id=company_id)
        return super(ActivityMonitorView, self).get_queryset()


class TextAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = TextSerializer
    queryset = TextAnswer.objects.all()


class RatingAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    queryset = RatingAnswer.objects.all()


class MCQAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = MCQSerializer
    queryset = MCQAnswer.objects.all()


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = QuestionDB.objects.all()

    def get_queryset(self, **kwargs):
        if not self.request.user.is_superuser:
            queryset = QuestionDB.objects.filter(asked_by=self.request.user)
            return queryset
        else:
            queryset = QuestionDB.objects.all()
            return queryset


class QuestionSet(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    model = QuestionDB
    lookup_field = "rel_question"
    # queryset = QuestionDB.objects.all()

    def perform_create(self, serializer):
        survey_obj = Survey.objects.get(id=self.kwargs['rel_question'])
        print(survey_obj)
        que_obj = serializer.save()
        que_obj.asked_by.add(self.request.user)
        survey_obj.question.add(que_obj)
        print(que_obj)

    def get_queryset(self, *args, **kwargs):
        if 'rel_question' in self.kwargs:
            queryset = self.model.objects.filter(rel_question=self.kwargs['rel_question'])
        else:
            queryset = self.model.objects.filter(rel_question__created_by=self.request.user)
        return queryset


class TimeLineSet(RetrieveUpdateDestroyAPIView, CreateAPIView):
    pass


class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = Survey.objects.filter(created_by=self.request.user)
            return queryset
        else:
            queryset = Survey.objects.all()
            return queryset
