"""employee_management URL Configuration"""

from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken import views as auth_token_views

urlpatterns = [
    url(r'', include('main.urls')),
    url(r'', include('employee.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', auth_token_views.obtain_auth_token),
]
