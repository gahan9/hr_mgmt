from django.conf.urls import url, include
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.conf.urls.static import static
from django.conf import settings
from django_filters.views import FilterView
from forms.common import LoginForm
from . import views

urlpatterns = [
    url(r'^login/', django_login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': '/login/'}, name='logout'),
    url(r'^create-company', views.CreateCompanyView.as_view(), name="create_company"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
