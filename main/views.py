from copy import deepcopy

from braces.views._access import SuperuserRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

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


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()


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


class PlanSelector(APIView):
    login_url = reverse_lazy('login')
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser, )
    template_name = 'field_rate/purchase_plan.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, **kwargs):
        serializer = self.serializer_class(partial=True)
        response_data = {'serializer': serializer, 'style': self.style}
        stage = int(kwargs['stage']) if 'stage' in kwargs else 0
        response_data['stage'] = stage
        return Response(response_data)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(partial=True)
        response_data = {'serializer': serializer, 'style': self.style}
        stage = int(kwargs['stage']) if 'stage' in kwargs else 0
        response_data['stage'] = stage
        print(">> Request:POST::DATA === {}".format(request.data))
        for field, value in request.data.items():
            if request.data[field]:
                response_data[field] = request.data[field]
        if stage == 1:
            plan_obj = Plan.objects.get(pk=response_data['has_plan'])
            role_level = 1 if plan_obj.plan_name == 2 else 2
            serializer = self.serializer_class(data=response_data)
            serializer.initial_data.update({'role': role_level})
            if serializer.is_valid():
                print("valid serializer")
                serializer.save()
                response_data['serializer'] = CompanySerializer
                return Response(response_data)
            else:
                messages.error(request, message="Error: Something bad happened. Reason: {}".format(serializer.errors    ))
                return Response(response_data)
                # return HttpResponseRedirect(reverse_lazy('select_plan', kwargs={'stage': 0}))
        else:
            return Response(response_data)
