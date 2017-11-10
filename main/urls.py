from django.conf.urls import url
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.conf.urls.static import static
from django.conf import settings

from forms.common import LoginForm
from . import views

urlpatterns = [
    url(r'^login/', django_login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': '/login/'}, name='logout'),
    url(r'^$', views.HomePageView.as_view(), name="home"),
    url(r'^employee-data/', views.EmployeeDataView.as_view(), name="employee_data"),
    url(r'^field-rate/', views.FieldRateView.as_view(), name="field_rate"),
    url(r'^upload_file/', views.FileUploadView.as_view(), name="file_upload"),
    url(r'^view_file/', views.EmployeeDataList.as_view(), name="view_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
