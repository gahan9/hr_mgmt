import codecs
import csv
import os
from collections import OrderedDict
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse, FileResponse
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_tables2.views import SingleTableView
from rest_framework.authtoken.models import Token
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from employee_management.settings import BASE_DIR
from employee.tables import *
from employee.serializers import *
from forms.common import *


def get_user_company(user):
    """
    Get company name from where user belong
    :param user: user object
    :return: company object of user
    """
    if hasattr(user, 'employee'):
        return user.employee.company_name
    elif hasattr(user, 'rel_company_user'):
        return user.rel_company_user
    else:
        return "OOps.. you are from nowhere.. Are you root? or you are lost?"


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Home page view of field rate
    """
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
    """
    File upload view for uploading user data from csv
    """
    login_url = reverse_lazy('login')
    form_class = FileUploadForm
    success_url = reverse_lazy('file_upload')
    template_name = "company/file_upload.html"

    @staticmethod
    def server_dump_setup():
        """
        setup directory for error handling
        :return: file location and name
        """
        dump_dir = os.path.join(BASE_DIR, "server_dump")  # BASE_DIR imported from settings
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H:%M:%S")
        file_name = "failure_{}.csv".format(timestamp)
        file_location = os.path.join(dump_dir, file_name)
        return file_location, file_name

    def post(self, request, *args, **kwargs):
        """
        override post method to create user after successful file upload
        :return:
            success: create user and display success message
            failure: allow user to download failed user list as csv
            ::TO BE CHANGE: failure needs to handle with ajax to show hybrid state in case of both success and failure
                            failure should display list of failed user in table instead of csv download
        """
        current_user = self.request.user
        current_user_company = get_user_company(current_user)
        user_file = self.request.FILES['file']
        category = self.request.POST['category']
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
                                            job_title=row['job_title'], category=category,
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
                # return FileResponse(open(failure_store_location, "rb"))
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
    """
    Custom form mixin for enabling filter in employee data view generated by django-tables2
    """

    def define_form(self):
        def get_form_field_type(f):
            if f == "user__email":
                return forms.CharField(required=False, label="Email")
            elif f == "user__first_name":
                return forms.CharField(required=False, label="First Name")
            elif f == "user__last_name":
                return forms.CharField(required=False, label="Last Name")
            return forms.CharField(required=False)

        attrs = OrderedDict((f, get_form_field_type(f)) for f in self.get_form_fields())
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
    """
    show employee data of company with search/filter option
    """
    login_url = reverse_lazy('login')
    model = Employee
    template_name = "company/employee_detail.html"
    table_class = EmployeeTable
    table_pagination = {'per_page': 15}
    search_fields = ['user__contact_number', 'user__first_name', 'user__last_name', 'user__email',
                     'job_title', 'street', 'city', 'country']

    def get_form_fields(self):
        """
        Enables filter for fields mentioned in list search_fields
        :return: list of fields for search
        """
        return self.search_fields

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


class SurveyManager(LoginRequiredMixin, AddFormMixin, SingleTableView):
    login_url = reverse_lazy('login')
    template_name = 'company/survey.html'
    model = Survey
    table_class = SurveyTable
    table_pagination = {'per_page': 15}
    search_fields = ['name', 'employee_group', 'question__question']

    def get_queryset(self):
        if not self.request.user.is_superuser:
            self.queryset = Survey.objects.filter(created_by=self.request.user)
        else:
            self.queryset = Survey.objects.all()
        return super(SurveyManager, self).get_queryset()

    def get_form_fields(self):
        return self.search_fields


class AddQuestion(APIView, LoginRequiredMixin):
    """    Add Question pop up    """
    login_url = reverse_lazy('login')
    template_name = 'company/add_question.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, *args, **kwargs):
        serializer = QuestionSerializer()
        return Response({'serializer': serializer, 'style': self.style})

    def post(self, request):
        current_user = self.request.user
        content_object = None
        response_data = {field: value for field, value in request.data.items()}
        answer_type = int(request.data['answer_type']) if 'answer_type' in request.data else None
        if answer_type == 0:  # MCQ answer
            options = request.data.getlist('mytext[]')
            content_object = MCQAnswer.objects.create(option=options)
            response_data['content_type'] = ContentType.objects.get_for_model(MCQAnswer).id
        elif answer_type == 1:  # Rating answer
            content_object = RatingAnswer.objects.create()
            response_data['content_type'] = ContentType.objects.get_for_model(RatingAnswer).id
        elif answer_type == 2:  # text answer
            content_object = TextAnswer.objects.create()
            response_data['content_type'] = ContentType.objects.get_for_model(TextAnswer).id
        serializer = QuestionSerializer(data=response_data, context={'request': request})
        if serializer.is_valid():
            que_obj = serializer.save()
            que_obj.asked_by.add(current_user)  # add user created in field
            if content_object:
                que_obj.content_object = content_object
                que_obj.save()
            message = "question created"
            messages.success(request, message=message)
        else:
            if content_object:
                print("deleting object....")
                content_object.delete()
            messages.error(request, message="Error: Something bad happened. Reason: {}".format(serializer.errors))
        return Response({'serializer': serializer, 'style': self.style})


class AddSurvey(APIView):
    login_url = reverse_lazy('login')
    # template_name = 'company/add_survey.html'
    template_name = 'company/_add_survey.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, **kwargs):
        step = int(kwargs['step']) if 'step' in kwargs else 0
        survey_id = int(kwargs['survey_id']) if 'survey_id' in kwargs else None
        if survey_id:
            instance = Survey.objects.get(id=survey_id)
            serializer = SurveySerializer(instance, context={'request': request})
        else:
            serializer = SurveySerializer()
        if not step:  # initialize survey
            return Response({'serializer': serializer, 'style': self.style, 'step': step, 'survey_id': survey_id, 'step_range': range(step)})
        elif step == 2:  # handle employee group entry
            return Response({'serializer': serializer, 'style': self.style, 'step': step, 'survey_id': survey_id, 'step_range': range(step)})
        elif step == 3:  # handle question entry
            question_set = QuestionDB.objects.filter(asked_by__rel_company_user=get_user_company(request.user)) | QuestionDB.objects.filter(benchmark=True)
            print(question_set)
            try:
                que_instance = QuestionDB.objects.filter(rel_question=Survey.objects.get(id=6))
            except Exception as e:
                print(e)
                que_instance = None
            serializer = QuestionSerializer()
            flag = "add_new" if 'add_new' in kwargs else None
            question_id = [i.id for i in que_instance] if que_instance else None
            return Response({'serializer': serializer, 'style': self.style, 'step': step, 'survey_id': survey_id,
                             'question_set': question_set, 'flag': flag, 'que_id': question_id, 'step_range': range(step)})
        elif step == 4:
            try:
                instance.start_date = default_start_time()
                instance.end_date = default_end_time()
                serializer = SurveySerializer(instance, context={'request': request})
            except NameError:
                return HttpResponse("Don't be over smart...")
            return Response({'serializer': serializer, 'style': self.style, 'step': step, 'survey_id': survey_id, 'step_range': range(step)})
        return Response({'serializer': serializer, 'style': self.style, 'step': step, 'survey_id': survey_id, 'step_range': range(step)})

    def post(self, request, **kwargs):
        print(kwargs)
        step = int(kwargs['step']) if 'step' in kwargs else 0
        survey_id = int(kwargs['survey_id']) if 'survey_id' in kwargs else None
        survey_id = None if survey_id == 0 else survey_id
        partial = False
        instance = None
        if survey_id:
            partial = True
            instance = Survey.objects.get(id=survey_id)
            instance.steps = step
        if step == 3:
            instance.question.clear()
            for question in request.data.getlist('question'):
                question_instance = QuestionDB.objects.get(id=question)
                question_instance.asked_by.add(request.user)
                instance.question.add(question_instance)
            serializer = SurveySerializer(instance=instance, data=request.data, context={'request': request},
                                          partial=partial)
        else:
            serializer = SurveySerializer(instance=instance, data=request.data, context={'request': request},
                                          partial=partial)
        if serializer.is_valid():
            survey_obj = serializer.save()
            question_set = QuestionDB.objects.filter(asked_by__rel_company_user=get_user_company(request.user))
            data = {'serializer': serializer, 'style': self.style, 'step': step+1, 'survey_id': survey_obj.id, 'question_set': question_set, 'step_range': range(step)}
            if step == 6:
                data['step'] = 'complete'
                survey_obj.complete = True
                survey_obj.steps = 5
                message = "created survey {} for publish".format(survey_obj.id)
                messages.success(request, message=message)
            else:
                message = 'created survey "{} (id - {})" with {} steps'.format(survey_obj.name, survey_obj.id, step)
                messages.success(request, message=message)
            return HttpResponseRedirect(redirect_to=reverse_lazy('add_survey', kwargs={'step': step+1, 'survey_id': survey_obj.id}))
        else:
            messages.error(request, message="Error: Something bad happened")
            return Response({'serializer': serializer, 'style': self.style})


class CreateSurvey(AddSurvey):
    template_name = 'company/add_survey.html'


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
                                            profile_image=self.request.FILES['profile_image'],
                                            role=set_role, has_plan=current_user.has_plan
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
    """
    Edit employee details
    """
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
    """
    Edit user detail associated with it's employee profile
    """
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


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete employee from system
    """
    login_url = reverse_lazy('login')
    model = UserModel
    success_message = "'%(name)s'  deleted..."
    success_url = reverse_lazy("view_data")

    def delete(self, request, *args, **kwargs):
        current_user = request.user
        company_id = get_user_company(current_user).id
        user_object = self.get_object()
        value_user = [user_object.contact_number, user_object.first_name, user_object.last_name]
        del_msg = "{}".format(value_user)
        activity_obj = ActivityMonitor.objects.create(remarks=del_msg, activity_type=2,
                                                      company_id=company_id,
                                                      performed_by=request.user.get_detail(),
                                                      affected_user=user_object.get_detail())
        print(activity_obj)
        message = 'User: {} (M: {}) deleted successfully'.format(user_object.first_name, user_object.contact_number)
        messages.success(request, message)
        return super(EmployeeDeleteView, self).delete(request, *args, **kwargs)


class ActivityMonitorView(LoginRequiredMixin, SingleTableView):
    """
    Display all activity performed in company administration
    """
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
