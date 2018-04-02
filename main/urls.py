from django.conf.urls import url, include
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework import routers

from main import views
from employee.viewsets import *

# register api with default router
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='usermodel')
router.register(r'employee', EmployeeViewSet, base_name='employee')
router.register(r'plans', views.PlanViewSet, base_name='plan')
router.register(r'company', views.CompanyViewSet, base_name='company')
router.register(r'question_database', QuestionViewSet, base_name='questiondb')
router.register(r'survey/response', SurveyResponseViewSet, base_name='surveyresponse')
router.register(r'survey', SurveyViewSet, base_name='survey')
router.register(r'news_feed', NewsFeedViewSet, base_name='newsfeed')

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/', RedirectView.as_view(url='/api/v1/')),
    url(r'^login/', django_login, {'template_name': 'common/login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': reverse_lazy('login')}, name='logout'),
    url(r'^create-company', views.CreateCompanyView.as_view(), name="create_company"),
    url(r'^select-plan/', views.PlanSelector.as_view(), name="select_plan"),
    # custom implemented api
    url(r'^api/v1/survey/$', SurveyViewSet.as_view({'get': 'list', 'post': 'create'}), name="survey_list"),
    url(r'^api/v1/survey/(?P<pk>[^/.]+)/$', SurveyViewSet.as_view(
      {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
      name="survey-detail"),
    url(r'^api/v1/survey/(?P<rel_question>\d+)/question/$', QuestionSet.as_view(), name="survey_question"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
