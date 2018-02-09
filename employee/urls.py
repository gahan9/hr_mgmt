from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from employee.views import QuestionAutocomplete
from . import views


urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name="home"),
    url(r'^create-user', views.CreateUserView.as_view(), name="create_user"),
    url(r'^delete-user/(?P<pk>\d+)/$', views.EmployeeDeleteView.as_view(), name="delete_user"),
    url(r'^activity_log/$', views.ActivityMonitorView.as_view(), name="activity_log"),
    url(r'^company-data/', views.EmployeeDataView.as_view(), name="employee_data"),
        url(r'^upload_file/', views.FileUploadView.as_view(), name="file_upload"),
        url(r'^view_data/', views.EmployeeDataList.as_view(), name="view_data"),
        url(r'^edit_user_profile/(?P<pk>\d+)/$', views.EditUserView.as_view(), name="edit_user_profile"),
        url(r'^password_reset/(?P<pk>\d+)/$', views.PasswordResetView.as_view(), name="password_reset"),
        url(r'^edit_employee_profile/(?P<pk>\d+)/$', views.EditEmployeeView.as_view(), name="edit_employee_profile"),
    url(r'^field-rate/', views.FieldRateView.as_view(), name="field_rate"),
        url(r'^survey/', views.SurveyManager.as_view(), name="survey_manage"),
            url(r'^add_survey/$', views.AddSurvey.as_view(), name="add_survey"),
            url(r'^add_survey/(?P<survey_id>\d+)/(?P<step>\d+)/$', views.AddSurvey.as_view(), name="add_survey"),
            url(r'^add_survey/add_new_question/', views.AddQuestion.as_view(), name="add_new_question"),
            url(r'^create_survey/$', views.CreateSurvey.as_view(), name="create_survey"),
            url(r'^create_survey/(?P<survey_id>\d+)/(?P<step>\d+)/$', views.CreateSurvey.as_view(), name="create_survey"),
            url(r'^create_survey/add_new_question/', views.AddQuestion.as_view(), name="create_new_question"),
    url(r'^question-autocomplete/$', QuestionAutocomplete,
        name='question-autocomplete',),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
