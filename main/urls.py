from django.conf.urls import url
from django.contrib.auth.views import login as django_login, logout as django_logout

from forms.common import LoginForm
from . import views

urlpatterns = [
    url(r'^login/', django_login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': '/'}, name='logout'),
    url(r'^$', views.HomePageView.as_view(), name="home"),
]
