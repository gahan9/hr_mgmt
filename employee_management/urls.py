"""employee_management URL Configuration"""

from django.conf.urls import url, include
from django.contrib import admin
from main.views import CustomAuthentication
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'', include('main.urls')),
    url(r'', include('employee.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', CustomAuthentication.as_view(), name='get_auth_token'),
    url(r'^chat/', include('chat.urls')),
    url(r'^api-docs/', include_docs_urls(title='Api doc')),
]
