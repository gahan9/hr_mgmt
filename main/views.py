from braces.views._access import SuperuserRequiredMixin

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http.response import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from employee.views import get_user_company
from forms.common import *
from main.serializers import *
from main.utility import *

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API ViewSet to get list of user, modify and update their profile
    ---
    `/api/v1/users/`
    get user detail if logged in user is

    - `super user`: access to all user
    - `hr`: access to all user within it's company
    - `employee`: access to only self profile

    `/api/v1/users/{pk}/`

    - retrieves profile of user for given `pk` if user is itself or fall within it's domain
    """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('employee__company_name', 'role')

    def get_queryset(self):
        current_user = self.request.user
        _pk = self.kwargs.get('pk', None)
        if hasattr(current_user, 'employee'):
            # if user is employee then only provide it'sown information
            queryset = self.queryset.filter(id=current_user.id)
        elif current_user.is_hr:
            # get list of all user under hr including hr itself
            queryset = self.queryset.filter(Q(employee__company_name__company_user=current_user)
                                            | Q(id=current_user.id))
            if _pk:
                # filter queryset if kwarg pk is passed
                queryset = queryset.filter(pk=_pk)
        elif current_user.is_superuser:
            # return list of all user if superuser is logged in
            queryset = self.queryset.filter(pk=_pk) if _pk else self.queryset
        else:
            queryset = self.queryset.filter(id=current_user.id)
        return queryset


class PlanViewSet(viewsets.ModelViewSet):
    """manage purchase plan package for company
    """
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    permission_classes = [IsAdminUser]


class CompanyViewSet(viewsets.ModelViewSet):
    """only superuser is allowed to access this data

    retrieve details of company HR
    """
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = [IsAdminUser]


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
                                      password=set_password_hash(form_data['password']),
                                      is_hr=form_data['role'],
                                      )
        company_obj = Company.objects.create(company_user=hr, name=form_data['name'],
                                             alternate_contact_no=form_data['alternate_contact_no'],
                                             alternate_email=form_data['alternate_email'],
                                             country=form_data['country'])
        messages.success(self.request, "HR {} with contact_number {} created successfully.".format(hr.first_name, hr.contact_number))
        return HttpResponseRedirect(reverse_lazy('create_company'))


class PlanSelector(APIView):
    """Form to auto select plan

    any one can proceed to purchase
    """
    login_url = reverse_lazy('login')
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, )
    template_name = 'field_rate/purchase_plan.html'
    renderer_classes = [TemplateHTMLRenderer]
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, **kwargs):
        serializer = self.serializer_class(partial=True)
        response_data = {'serializer': serializer, 'style': self.style}
        return Response(response_data)

    def post(self, request, **kwargs):
        serializer = self.serializer_class(partial=True)
        response_data = {'serializer': serializer, 'style': self.style}
        for field, value in request.data.items():
            if request.data[field]:
                if field == "profile_image":
                    response_data[field] = request.FILES[field]
                else:
                    response_data[field] = request.data[field]
        serializer = self.serializer_class(data=response_data)
        serializer.initial_data.update({'role': 2})
        if serializer.is_valid():
            print("valid serializer")
            user_serializer = serializer.save()
            company_serializer = CompanySerializer(
                data={'company_user': user_serializer.id,
                      'name': user_serializer.get_full_name()})
            if company_serializer.is_valid():
                print("valid company serializer")
                company_serializer.save()
                messages.success(request, message="Plan activated Successfully!")
            else:
                print("invalid company serializer")
                msg = "Error: Something bad happened. Reason: {}".format(company_serializer.errors)
                messages.error(request, message=msg)
        else:
            print("invalid user serializer")
            msg = "Error: Something bad happened. Reason: {}".format(serializer.errors)
            messages.error(request, message=msg)
        return Response(response_data)


class CustomAuthentication(ObtainAuthToken):
    """Custom Token Authentication

    provide user detail along with the details of it's creator (HR)  -- for android APP (employee only)
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # print(user)
        token, created = Token.objects.get_or_create(user=user)
        response_data = user.detail
        response_data['token'] = token.key
        response_data['profile_image'] = ''.join(
            ['http://', get_current_site(request).domain, user.profile_image.url]
        ) if user.profile_image else ''
        try:
            if hasattr(user, 'employee'):
                _creator_hr = user.get_creator_detail
                if _creator_hr['hr_profile_image']:
                    _creator_hr['hr_profile_image'] = ''.join(
                        ['http://', get_current_site(request).domain, _creator_hr['hr_profile_image']]
                    )
                response_data.update(_creator_hr)
        except Exception as e:
            print("Auth Exception {} for user".format(e))
        # print(response_data)
        return Response(response_data)
