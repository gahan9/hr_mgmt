import codecs
import csv
from collections import OrderedDict

import requests
from braces.views import JSONResponseMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.serializers import serialize
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_tables2.views import SingleTableView

from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.utils import plot_graph
from employee_management.settings import BASE_DIR
from employee.tables import *
from employee.serializers import *
from forms.common import *
from main.utility import *


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
        timestamp = timezone.now().strftime("%Y_%m_%d_%H:%M:%S")
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
        # fieldnames to read from csv file
        fieldnames = ['contact_number', 'first_name', 'last_name', 'email', 'alternate_email',
                      'alternate_contact_no', 'gender', 'job_title', 'street', 'zip_code', 'city', 'country',
                      'role', 'password', 'error_reason']
        try:
            csv_read = csv.DictReader(codecs.iterdecode(user_file, 'utf-8'))
            failure_store_location, file_name = self.server_dump_setup()
            for row in csv_read:
                _contact_number = row.get('contact_number', '')
                password_generated = row.get('first_name', '') + "@" + _contact_number
                _pass = row.get('password', None)
                password = _pass if _pass else password_generated
                try:
                    user_obj = UserModel.objects.create(
                        contact_number=_contact_number,
                        password=set_password_hash(password),
                        email=row.get('email', None),
                        gender=row.get('gender', 'M'),
                        first_name=row.get('first_name'),
                        last_name=row.get('last_name'),
                        role=3  # employee
                    )
                    ActivityMonitor.objects.create(activity_type=0, company_id=current_user_company.id,
                                                   performed_by=current_user.detail,
                                                   affected_user=user_obj.detail, bulk_create=True)
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
                    row['error_reason'] = "Unable to add company because User with the same detail already exist more-detail:{}".format(
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
                msg = "Error: {} user(s) failed to create from {}".format(failed_user, user_file)
                messages.error(request, msg)
                response = HttpResponse(open(failure_store_location, "rb"), content_type='text/csv')
                response['Content-Disposition'] = "attachment; filename={filename}".format(
                    filename=file_name
                )
                # response['Content-Length'] = open(failure_store_location, "rb").tell()
                # return FileResponse(open(failure_store_location, "rb"))
                return response
        except Exception as file_error:
            print("File-Error-----> {}".format(file_error))
            msg = "Error: Invalid file type or header : '{}' . Please upload valid csv file".format(user_file)
            messages.error(request, msg)
            # return HttpResponseRedirect("")
        if no_of_user > 0:
            msg = "{} user(s) created successfully".format(no_of_user)
            messages.success(request, msg)
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
        if hasattr(current_user, 'employee'):
            company_id = Company.objects.get(company_user=current_user.employee.added_by)
        else:
            # if user in this exception means user itself a company-owner
            company_id = Company.objects.get(company_user=current_user)
        if self.queryset is None:
            # returns queryset for user list with equal or lower role
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
            self.queryset = self.model.objects.filter(created_by=self.request.user)
        else:
            self.queryset = self.model.objects.all()
        return super(SurveyManager, self).get_queryset()

    def get_form_fields(self):
        return self.search_fields


class AddQuestion(APIView, LoginRequiredMixin):
    """Add New Question to Database

    """
    login_url = reverse_lazy('login')
    serializer_class = QuestionSerializer
    template_name = 'company/add_question.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, *args, **kwargs):
        return Response({'serializer': self.serializer_class(), 'style': self.style})

    def post(self, request):
        current_user = self.request.user
        content_object = None
        response_data = {field: value for field, value in request.data.items()}
        """
        # Below block is disabled.. it is for choosing various answer type of question
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
        """
        serializer = QuestionSerializer(data=response_data, context={'request': request})
        if serializer.is_valid():
            que_obj = serializer.save()
            que_obj.asked_by.add(current_user)  # add user created in field
            """
            # Below block is disabled.. it is for choosing various answer type of question
            if content_object:
                que_obj.content_object = content_object
            """
            que_obj.save()
            message = "question created"
            messages.success(request, message=message)
        else:
            """
            # Below block is disabled.. it is for choosing various answer type of question
            if content_object:
                print("deleting object....")
                content_object.delete()
            """
            messages.error(request, message="Error: Something bad happened. Reason: {}".format(serializer.errors))
        return Response({'serializer': serializer, 'style': self.style})


class AddSurvey(LoginRequiredMixin, APIView):
    # NOTE: depricated method.... to be removed soon.....
    login_url = reverse_lazy('login')
    # template_name = 'company/add_survey.html'
    template_name = 'company/_add_survey.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, **kwargs):
        _current_user = request.user  # current logged in user
        _user_company = get_user_company(_current_user)  # get current user's company
        step = int(kwargs.get('step', 0))  # get current step to proceed
        survey_id = int(kwargs.get('survey_id', 0))
        # filter question set for created by own and benchmark question
        question_set = QuestionDB.objects.filter(
            Q(asked_by__rel_company_user=_user_company) | Q(benchmark=True))
        question_id = [i.id for i in question_set] if question_set else None

        if survey_id:
            instance = Survey.objects.get(id=survey_id)
            serializer = SurveySerializer(instance, context={'request': request})
        else:
            serializer = SurveySerializer()

        # set up default response
        _response_data = {'serializer'  : serializer, 'style': self.style, 'step': step,
                          'survey_id'   : survey_id, 'step_range': range(step),
                          'question_set': question_set, 'que_id': question_id
                          }
        if not step:  # initialize survey
            return Response(_response_data)
        elif step == 2:  # handle employee group entry
            return Response(_response_data)
        elif step == 3:  # handle question entry
            serializer = QuestionSerializer()
            _response_data['serializer'] = serializer
            _response_data['flag'] = "add_new" if 'add_new' in kwargs else None
            return Response(_response_data)
        elif step == 4:
            try:
                instance.start_date = default_start_time()
                instance.end_date = default_end_time()
                serializer = SurveySerializer(instance, context={'request': request})
            except NameError:
                return HttpResponse("Don't be over smart...")
            _response_data['serializer'] = serializer
            return Response(_response_data)
        return Response(_response_data)

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
    login_url = reverse_lazy('login')
    template_name = 'add_survey.html'


class SurveyBenchmark(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'benchmark.html'


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
        print(self.request.FILES)
        _profile_img = self.request.FILES.get('profile_image', '')
        user_obj = UserModel.objects.create(contact_number=form_data['contact_number'], email=form_data['email'],
                                            first_name=form_data['first_name'], last_name=form_data['last_name'],
                                            password=set_password_hash(form_data['password']),
                                            profile_image=_profile_img,
                                            role=set_role, has_plan=current_user.has_plan
                                            )
        activity_obj = ActivityMonitor.objects.create(activity_type=0, performed_by=current_user.detail,
                                                      company_id=current_user_company.id,
                                                      affected_user=user_obj.detail)
        Employee.objects.create(user=user_obj, company_name=current_user_company,
                                job_title=form_data['job_title'],
                                alternate_email=form_data['alternate_email'],
                                alternate_contact_no=form_data['alternate_contact_no'],
                                street=form_data['street'], zip_code=form_data['zip_code'],
                                city=form_data['city'], country=form_data['country'],
                                added_by=current_user
                                )
        _msg = "User {} created successfully.".format(user_obj.get_full_name())
        messages.success(self.request, _msg)
        return HttpResponseRedirect(reverse_lazy('create_user'))

    def form_invalid(self, form):
        _msg = "Error: invalid data... {}".format(form.errors)
        messages.error(self.request, _msg)
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
        current_user = self.request.user
        user_object = Employee.objects.get(id=self.kwargs['pk']).user
        ActivityMonitor.objects.create(activity_type=1, company=current_user.get_company,
                                       performed_by=self.request.user.detail,
                                       affected_user=user_object.detail)
        return super(EditEmployeeView, self).form_valid(form)

    def form_invalid(self, form):
        current_user = self.request.user
        user_object = Employee.objects.get(id=self.kwargs['pk']).user
        ActivityMonitor.objects.create(activity_type=1, company=current_user.get_company,
                                       status=False,
                                       performed_by=current_user.detail,
                                       affected_user=user_object.detail)
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

    def get_context_data(self, **kwargs):
        context = super(EditUserView, self).get_context_data(**kwargs)
        context.update({"pass_key": self.kwargs['pk']})
        return context

    def form_valid(self, form, **kwargs):
        current_user = self.request.user
        user_object = UserModel.objects.get(id=self.kwargs['pk'])
        company = get_user_company(current_user)
        activity_obj = ActivityMonitor.objects.create(activity_type=1,
                                                      company_id=company.id,
                                                      performed_by=current_user.detail,
                                                      affected_user=user_object.detail)
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
                                                      performed_by=request.user.detail,
                                                      affected_user=user_object.detail)
        message = 'User: {} (M: {}) deleted successfully'.format(user_object.get_full_name(), user_object.contact_number)
        messages.success(request, message)
        return super(EmployeeDeleteView, self).delete(request, *args, **kwargs)


class ActivityMonitorView(LoginRequiredMixin, SingleTableView):
    """
    Display all activity performed in company administration
    """
    login_url = reverse_lazy('login')
    table_class = ActivityTable
    model = ActivityMonitor
    template_name = "company/activity_log.html"
    table_pagination = {'per_page': 15}

    def get_queryset(self):
        current_user = self.request.user
        company_id = get_user_company(current_user).id
        if self.queryset is None:
            self.queryset = ActivityMonitor.objects.filter(company_id=company_id)
        return super(ActivityMonitorView, self).get_queryset()


class PasswordResetView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    template_name = 'company/edit_user.html'
    model = UserModel
    success_url = reverse_lazy('view_data')
    form_class = ResetPasswordForm
    success_message = "Details updated successfully."

    def form_valid(self, form, **kwargs):
        current_user = self.request.user
        user_object = UserModel.objects.get(id=self.kwargs['pk'])
        company_id = get_user_company(current_user).id
        activity_obj = ActivityMonitor.objects.create(activity_type=1, remarks="Password Changed",
                                                      company_id=company_id,
                                                      performed_by=self.request.user.detail,
                                                      affected_user=user_object.detail)
        return super(PasswordResetView, self).form_valid(form)


class NewsFeedManager(LoginRequiredMixin, AddFormMixin, SingleTableView):
    login_url = reverse_lazy('login')
    template_name = 'company/news_feed.html'
    model = NewsFeed
    table_class = NewsFeedTable
    table_pagination = {'per_page': 15}
    search_fields = ['title', 'feed']
    ordering = ['-date_created']

    def get_queryset(self):
        _current_user = self.request.user
        if not _current_user.is_superuser:
            self.queryset = self.model.objects.filter(created_by=_current_user)
        else:
            self.queryset = self.model.objects.all()
        return super(NewsFeedManager, self).get_queryset()

    def get_form_fields(self):
        return self.search_fields


class CreateNewsFeed(LoginRequiredMixin, APIView):
    login_url = reverse_lazy('login')
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = NewsFeedSerializer
    model = NewsFeed
    success_url = reverse_lazy('manage_news_feed')
    template_name = 'company/create_news_feed.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request):
        serializer = self.serializer_class()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        serializer.save()
        return redirect(self.success_url)


class NewsFeedDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete NewsFeed from system
    """
    login_url = reverse_lazy('login')
    model = NewsFeed
    success_url = reverse_lazy("manage_news_feed")

    def delete(self, request, *args, **kwargs):
        current_user = request.user
        company_id = get_user_company(current_user).id
        selected_object = self.get_object()
        value_set = [selected_object.title, selected_object.feed]
        del_msg = "{}".format(value_set)
        activity_obj = ActivityMonitor.objects.create(remarks=del_msg, activity_type=2,
                                                      company_id=company_id,
                                                      performed_by=request.user.detail)
        print(activity_obj)
        message = 'NewsFeed: {} (Feed: {}) deleted successfully'.format(selected_object.title, selected_object.feed)
        messages.success(request, message)
        return super(NewsFeedDeleteView, self).delete(request, *args, **kwargs)


class SurveyDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete Survey from system
    """
    login_url = reverse_lazy('login')
    model = Survey
    success_url = reverse_lazy("survey_manage")

    def delete(self, request, *args, **kwargs):
        current_user = request.user
        company_id = get_user_company(current_user).id
        selected_object = self.get_object()
        value_set = [selected_object.name, selected_object.steps]
        del_msg = "{}".format(value_set)
        activity_obj = ActivityMonitor.objects.create(remarks=del_msg, activity_type=2,
                                                      company_id=company_id,
                                                      performed_by=request.user.detail)
        print(activity_obj)
        message = 'Survey: {} deleted successfully'.format(selected_object.name)
        messages.success(request, message)
        return super(SurveyDeleteView, self).delete(request, *args, **kwargs)


class SettingsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'company/settings.html'


class SampleView(JSONResponseMixin, BaseDetailView):
    def get(self, request, *args, **kwargs):
        with open(os.path.join(settings.MEDIA_ROOT, 'structure.json'), 'r') as fp:
            content = json.load(fp)
        return self.render_json_response(content)


class BenchmarkMap(TemplateView):
    template_name = 'map.html'
    GEOCODE_API_KEY = "AIzaSyBn2U40eWRFJtdcbBuA_ckU0CAb3CcqO8Y"
    GEOCODE_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    def _request(self, **kwargs):
        address = kwargs.get("address", "")
        payload = {"key": self.GEOCODE_API_KEY, "address": address}
        response = requests.get(self.GEOCODE_BASE_URL, params=payload)
        result = response.json().get("results", None)
        return result

    def update_geo_location(self, address):
        geo_instance, created = GeoLocations.objects.get_or_create(address=address)
        if created:
            result = self._request(address=address)
            if result:
                response = result[0].get('geometry').get('location')
                lat, lng = response.get('lat', None), response.get('lng', None)
                geo_instance.lat = lat
                geo_instance.lng = lng
                geo_instance.save()
        return geo_instance

    def get_context_data(self, **kwargs):
        context = super(BenchmarkMap, self).get_context_data(**kwargs)
        _query_params = kwargs
        survey_id = int(_query_params.get('survey_id', 0))
        question_id = int(_query_params.get('question_id', 0))
        if survey_id and question_id:
            _response_data = {"survey_id": survey_id, "question_id": question_id}
            _survey_instance = Survey.objects.get(pk=survey_id)
            _question = _survey_instance.benchmark.get(question_id, None)
            if _question:
                city_data = []
                for i in _question.get('city_response'):
                    city = i['city']
                    geo_instance = self.update_geo_location(address=city)
                    lat, lng = geo_instance.lat, geo_instance.lng
                    city_score = _survey_instance.filter_benchmark(city=city).get(question_id)

                    city_info = {'city': city,
                                 'average_rating': city_score['average_rating'],
                                 'total_responses': i['responses'],
                                 'lat' : lat, 'lng' : lng}
                    city_data.append(city_info)
                # _response_data['cities'] = {'results': city_data}
                _response_data['cities'] = json.dumps(city_data)
                _response_data['city_response'] = _question.get('city_response')
                _response_data['city_response'] = city_data
                # print(_response_data)
            context.update(_response_data)
        return context


class QuestionGraph(TemplateView):
    template_name = 'graph.html'

    def get_context_data(self, **kwargs):
        context = super(QuestionGraph, self).get_context_data(**kwargs)
        _query_params = self.request.GET
        survey_id = int(kwargs.get('survey_id', 0))
        question_id = int(kwargs.get('question_id', 0))
        city = _query_params.get('city', None)
        graph_mode = _query_params.get('graph_mode', 'city_response')
        x, y = [], []
        x_title, y_title, graph_type, traces = "X", "Y", "bar", None
        if survey_id and question_id:
            try:
                _survey_instance = Survey.objects.get(pk=survey_id)
                if city:

                    import plotly.graph_objs as go
                    if graph_mode == "city_response":
                        graph_type = "bar"
                        x_title = "Ratings from {}".format(city)
                        y_title = "Number of Ratings"
                        y1 = []
                        survey_response = _survey_instance.benchmark.get(question_id)
                        ratings_count = survey_response.get('rates')
                        filtered_survey_responses = _survey_instance.filter_benchmark(city=city).get(question_id)
                        filtered_ratings_count = filtered_survey_responses.get('rates')
                        rate_scale = filtered_survey_responses.get('rate_scale')
                        context['comments'] = filtered_survey_responses.get('comments')
                        for i in range(1, rate_scale+1):
                            x.append(i)
                            y.append(filtered_ratings_count.get(i, 0))
                            y1.append(ratings_count.get(i, 0))
                        t1 = go.Bar(x=x, y=y, name=x_title,
                                    marker=dict(color='rgb(204,204,204)',))
                        t2 = go.Bar(x=x, y=y1, name="Ratings from all city",
                                    marker=dict(color='#bc8e76',))
                        traces = [t1, t2]
                else:
                    x_title, y_title = "City", "Total Response"
                    _question = _survey_instance.benchmark.get(question_id, None)
                    if _question:
                        x = _question.get('cities', None)
                        y = []
                        for i in x:
                            y.append(_survey_instance.filter_benchmark(city=i).get(question_id).get('total_responses'))
                    else:
                        # messages.error(self.request, "Invalid survey question")
                        city_dict = list(_survey_instance.get_city_response_count)
                        for i in city_dict:
                            x.append(i.get('city'))
                            y.append(i.get('responses'))
                        graph_type = "scatter"
                # plotting graph
                context['graph'] = plot_graph(x=list(x), y=y, x_title=x_title, y_title=y_title, graph_type=graph_type, traces=traces)
                context['question_title'] = QuestionDB.objects.get(pk=question_id).question
            except Survey.DoesNotExist:
                messages.error(self.request, "Invalid survey id")
        return context
