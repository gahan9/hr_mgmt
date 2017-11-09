from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView, FormView, ListView
from django.urls import reverse_lazy
from django_tables2.views import MultiTableMixin

from forms.common import FileUploadForm
from main.models import FileUpload
from main.tables import FileUploadTable


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


class FileUploadView(FormView):
    form_class = FileUploadForm
    success_url = reverse_lazy('file_upload')
    template_name = "file_upload.html"

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, 'File uploaded successfully!')
        return super(FileUploadView, self).form_valid(form)


class FileListView(LoginRequiredMixin, MultiTableMixin, ListView):
    login_url = reverse_lazy('api-root')
    queryset = FileUpload.objects.order_by('-id')
    template_name = "table_show.html"
    tables = [FileUploadTable(FileUpload.objects.all())]
    table_pagination = {'per_page': 6}
    model = FileUpload
    # context_object_name = "files"
