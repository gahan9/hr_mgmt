from django.conf.urls import url, include
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.conf.urls.static import static
from django.conf import settings
from django_filters.views import FilterView
from rest_framework import routers

from forms.common import LoginForm
from . import views
from employee.views import *

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'employee', EmployeeViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'question_database', QuestionViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^login/', django_login, {'template_name': 'common/login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': '/login/'}, name='logout'),
    url(r'^create-company', views.CreateCompanyView.as_view(), name="create_company"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
