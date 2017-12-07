from braces.views._access import SuperuserRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from rest_framework import viewsets

from employee.views import get_user_company
from forms.common import *
from main.serializers import *

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('employee__company_name', 'role')

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = UserModel.objects.filter(employee__company_name=get_user_company(self.request.user.rel_company_user))
            print(queryset)
            return queryset
        else:
            queryset = UserModel.objects.all()
            return queryset


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class CreateCompanyView(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):
    """ view set to create company """
    login_url = reverse_lazy('login')
    template_name = "field_rate/create_company.html"
    form_class = CreateCompanyForm
    success_url = reverse_lazy('create_company')

    def form_valid(self, form):
        form_data = form.cleaned_data
        hr = UserModel.objects.create(contact_number=form_data['contact_number'], email=form_data['email'],
                                      first_name=form_data['first_name'], last_name=form_data['last_name'],
                                      password=make_password(form_data['password']),
                                      is_hr=form_data['role'],
                                      )
        company_obj = Company.objects.create(company_user=hr, name=form_data['name'],
                                             alternate_contact_no=form_data['alternate_contact_no'],
                                             alternate_email=form_data['alternate_email'],
                                             country=form_data['country'])
        messages.success(self.request, "HR {} with contact_number {} created successfully.".format(hr.first_name, hr.contact_number))
        return HttpResponseRedirect(reverse_lazy('create_company'))
        # return super(CreateCompanyView, self).form_valid(form)
