from django.conf.urls import url, include
from django.contrib.auth.views import login as django_login, logout as django_logout
from django.conf.urls.static import static
from rest_framework import routers

from main import views
from employee.viewsets import *

# register api with default router
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'employee', EmployeeViewSet)
router.register(r'plans', views.PlanViewSet)
router.register(r'company', views.CompanyViewSet)
router.register(r'question_database', QuestionViewSet)
router.register(r'answers/mcq', MCQAnswerViewSet)
router.register(r'answers/rating', RatingAnswerViewSet)
router.register(r'answers/text', TextAnswerViewSet)
router.register(r'survey/response', SurveyResponseViewSet)
router.register(r'surveys', SurveyViewSet)
# router.register(r'survey/{pk}/question/$', QuestionSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^login/', django_login, {'template_name': 'common/login.html', 'authentication_form': LoginForm}, name='login'),
    url(r'^logout/', django_logout, {'next_page': '/login/'}, name='logout'),
    url(r'^create-company', views.CreateCompanyView.as_view(), name="create_company"),
    url(r'^select-plan/(?P<stage>\d+)/$', views.PlanSelector.as_view(), name="select_plan"),
    # custom implemented api
    url(r'^api/survey/$', SurveyViewSet.as_view({'get': 'list', 'post': 'create'}), name="survey-list"),
    url(r'^api/survey/(?P<pk>[^/.]+)/$', SurveyViewSet.as_view(
      {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
      name="survey-detail"),
    url(r'^api/survey/(?P<rel_question>\d+)/question/$', QuestionSet.as_view(), name="survey_question"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
