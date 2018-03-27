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

    get user detail
    root: all user
    hr: all user within it's company
    employee: only self profile
    """
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('employee__company_name', 'role')

    def get_queryset(self):
        current_user = self.request.user
        _pk = self.kwargs.get('pk', None)
        if hasattr(current_user, 'employee'):
            queryset = self.queryset.filter(id=current_user.id)
        elif current_user.is_hr:
            # get list of all user under hr including hr itself
            queryset = self.queryset.filter(Q(employee__company_name__company_user=current_user)
                                            | Q(id=current_user.id))
            if _pk:
                queryset = queryset.filter(pk=_pk)
        elif current_user.is_superuser:
            # return list of all user if superuser is logged in
            queryset = self.queryset.filter(pk=_pk) if _pk else self.queryset
        return queryset


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()


class CompanyViewSet(viewsets.ModelViewSet):
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
        stage = int(kwargs['stage']) if 'stage' in kwargs else 0
        response_data['stage'] = stage
        if stage == 0:
            return Response(response_data)
        elif stage == 1:
            # uncomment below line to enable entry if company purchase (Enterprise Plan)
            # response_data['serializer'] = CompanySerializer(partial=True)
            return Response(response_data)
        else:
            return Http404

    def post(self, request, **kwargs):
        serializer = self.serializer_class(partial=True)
        response_data = {'serializer': serializer, 'style': self.style}
        stage = int(kwargs['stage']) if 'stage' in kwargs else 0
        response_data['stage'] = stage
        print(">> KWARGS === {}".format(kwargs))
        print(">> Request:POST::DATA === {}".format(request.data.items()))
        for field, value in request.data.items():
            if request.data[field]:
                if field == "profile_image":
                    print(self.request.FILES)
                    response_data[field] = self.request.FILES[field]
                # elif field == "password":
                #     response_data[field] = computeMD5hash(self.request.data[field])
                else:
                    response_data[field] = self.request.data[field]
        print(response_data)
        if stage == 1:
            # plan_obj = Plan.objects.get(pk=response_data['has_plan'])
            # role_level = 1 if plan_obj.plan_name == 2 else 2
            serializer = self.serializer_class(data=response_data)
            serializer.initial_data.update({'role': 2})
            if serializer.is_valid():
                print("valid serializer")
                user_serializer = serializer.save()
                #  ## settings for (Enterprise Plan) --begin here
                # uncomment below line(s) to enable entry if company purchase (Enterprise Plan)
                # response_data['serializer'] = CompanySerializer
                # comment below line(s)
                company_serializer = CompanySerializer(
                    data={'company_user': user_serializer.id,
                          'name': user_serializer.get_full_name()})
                if company_serializer.is_valid():
                    company_serializer.save()
                else:
                    msg = "Error: Something bad happened. Reason: {}".format(company_serializer.errors)
                    messages.error(request, message=msg)
                    response_data['stage'] -= 1
                    return Response(response_data)
                response_data['stage'] = 5
                # ## settings for (Enterprise Plan) --- Ends here
                messages.success(request, message="Plan activated Successfully!")
                return Response(response_data)
            else:
                msg = "Error: Something bad happened. Reason: {}".format(serializer.errors)
                messages.error(request, message=msg)
                response_data['stage'] -= 1
                return Response(response_data)
                # return HttpResponseRedirect(reverse_lazy('select_plan', kwargs={'stage': 0}))
        elif stage == 2:
            print(request.data)
            serializer = CompanySerializer(data=response_data, partial=True)
            serializer.initial_data.update({'company_user': self.request.user.id})
            if serializer.is_valid():
                messages.success(request, message="Successfully created company profile.")
                return Response(response_data)
            else:
                messages.error(request, message="Error: Something bad happened. Reason: {}".format(serializer.errors))
                return Response(response_data)
        else:
            return HttpResponseRedirect(reverse_lazy('select_plan', kwargs={'stage': 0}))


class CustomAuthentication(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response_data = user.get_detail()
        response_data['token'] = token.key
        response_data['profile_image'] = ''.join(
            ['http://', get_current_site(request).domain, user.profile_image.url]
        ) if user.profile_image else ''
        try:
            _creator_hr = user.get_creator
            if _creator_hr['hr_profile_image']:
                _creator_hr['hr_profile_image'] = ''.join(
                    ['http://', get_current_site(request).domain, _creator_hr['hr_profile_image']]
                )
            response_data.update(_creator_hr)
            return Response(response_data)
        except Exception as e:
            print("Auth Exception {} for user".format(e))
            return Response(response_data)
