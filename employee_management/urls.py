"""employee_management URL Configuration"""

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'', include('main.urls')),
    url(r'', include('employee.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
