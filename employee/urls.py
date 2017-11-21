from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view(), name="home"),
    url(r'^create-user', views.CreateUserView.as_view(), name="create_user"),
    url(r'^company-data/', views.EmployeeDataView.as_view(), name="employee_data"),
        url(r'^upload_file/', views.FileUploadView.as_view(), name="file_upload"),
        url(r'^view_data/', views.EmployeeDataList.as_view(), name="view_data"),
    url(r'^field-rate/', views.FieldRateView.as_view(), name="field_rate"),
        url(r'^survey/', views.SurveyManager.as_view(), name="survey_manage"),
            url(r'^add_survey/', views.AddSurvey.as_view(), name="add_survey"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
