from django.views.generic.edit import UpdateView, FormMixin
from rest_framework import viewsets

from employee.serializers import *
from main.views import *


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
        try:
            current_user_company = Company.objects.get(company_user=current_user)
        except:
            current_user_company = Company.objects.get(id=Employee.objects.get(user=current_user).id)
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
                    Employee.objects.create(user=user_obj, company_name=current_user_company,
                                            alternate_contact_no=row['alternate_contact_no'],
                                            alternate_email=row['alternate_email'],
                                            job_title=row['job_title'], street=row['street'],
                                            zip_code=row['zip_code'], city=row['city'],
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
                    row['error_reason'] = "Unable to add company because User with the same email already exist more-detail:{}".format(duplicate_error)
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
    template_name = "company/table_show.html"
    table_class = EmployeeTable
    table_pagination = {'per_page': 15}

    def get_form_fields(self):
        return ['user__first_name', 'user__last_name', 'user__contact_number', 'user__email', 'job_title', 'street', 'city', 'country']

    def get_queryset(self):
        current_user = self.request.user
        try:
            company_id = Company.objects.get(id=Employee.objects.get(user=current_user).company_name.id)
        except Exception as e:
            # if user in this exception means user itself a company-owner
            print(e)
            company_id = Company.objects.get(company_user=current_user).id
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

    # def form_valid(self, form):
    #     print("here... {}".format(self.object))
    #     return super(AddSurvey, self).form_valid(form)


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
        hr = UserModel.objects.create(contact_number=form_data['contact_number'], email=form_data['email'],
                                      first_name=form_data['first_name'], last_name=form_data['last_name'],
                                      password=make_password(form_data['password']),
                                      role=set_role,
                                      )
        Employee.objects.create(user=hr, company_name=current_user_company,
                                job_title=form_data['job_title'],
                                alternate_email=form_data['alternate_email'],
                                alternate_contact_no=form_data['alternate_contact_no'],
                                street=form_data['street'], zip_code=form_data['zip_code'],
                                city=form_data['city'], country=form_data['country']
                                )
        messages.success(self.request, "HR {} {} created successfully.".format(hr.first_name, hr.last_name))
        return HttpResponseRedirect(reverse_lazy('create_user'))

    def form_invalid(self, form):
        msg = "Error: invalid data... {}".format(form.errors)
        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('create_user'))


class EditUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('login')
    template_name = 'company/edit_user.html'
    model = Employee
    success_url = reverse_lazy('view_data')
    form_class = CreateUserForm
    success_message = "Details updated successfully."


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
