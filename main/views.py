import os
import csv
import codecs
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django_tables2.views import MultiTableMixin, SingleTableMixin

from forms.common import FileUploadForm
from main.models import FileUpload, EmployeeData, EmployeeDataFilter
from main.tables import EmployeeDataTable
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
        x = self.request.FILES['file']
        csv_read = csv.DictReader(codecs.iterdecode(x, 'utf-8'))
        failure_store_location, file_name = self.server_dump_setup()
        csv_file = open(failure_store_location, 'w')
        fieldnames = ['first_name', 'last_name', "mobile", "email", "error_reason"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in csv_read:
            password = row['first_name'] + "@" + row['mobile']
            try:
                user_obj = User.objects.create(
                    username=row['email'],
                    password=make_password(password),
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                EmployeeData.objects.create(user=user_obj, contact_no=row['mobile'])
            except IntegrityError:
                row['error_reason'] = "Unable to add employee because User with the same email already exist"
                writer.writerow(row)
            except Exception as e:
                row['error_reason'] = e
                writer.writerow(row)
        csv_file.close()
        if failure_store_location:
            response = HttpResponse(open(failure_store_location, "rb"), content_type='text/csv')
            response['Content-Disposition'] = "attachment; filename={filename}".format(
                filename=file_name
            )
            return response
        return super(FileUploadView, self).post(request, *args, **kwargs)


class EmployeeDataList(LoginRequiredMixin, MultiTableMixin, FilterView):
    login_url = reverse_lazy('login')
    model = EmployeeData
    template_name = "table_show.html"
    tables = [EmployeeDataTable(EmployeeData.objects.all().order_by('-id'))]
    table_pagination = {'per_page': 6}
    filterset_class = EmployeeDataFilter
    # context_object_name = "files"
