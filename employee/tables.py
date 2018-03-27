import django_tables2 as tables
from django.utils.html import escape
from django.utils.safestring import mark_safe

from employee.models import *


class EmployeeTable(tables.Table):
    """
    django-tables2 used for Employee model to list employee details
    """
    # id = tables.LinkColumn('employee:edit_data', args=[Employee('pk')])
    id = tables.TemplateColumn('<a href="/edit_employee_profile/{{record.id}}">{{record.id}}</a>')
    # contact_number = tables.Column(accessor='user.contact_number', verbose_name='Mobile Number')
    contact_number = tables.TemplateColumn(
        accessor='user.contact_number',
        template_code='<a href="/edit_user_profile/{{record.user.id}}">{{record.user.contact_number}}</a>')
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    email = tables.Column(accessor='user.email', verbose_name='Email Address')
    role = tables.Column(accessor='user.role', verbose_name='Role')
    category = tables.Column(verbose_name='Region')
    added_by = tables.Column(verbose_name='Created by')
    delete = tables.TemplateColumn(
        template_code="""<form action="{% url 'delete_user' pk=record.user.pk %}" method="POST"> {% csrf_token %}
                            <input class="btn btn-default btn-danger" type="submit" value="Delete"/>
                        </form>""", orderable=False)

    class Meta:
        model = Employee
        fields = ['id', 'contact_number', 'first_name', 'last_name', 'email', 'job_title',
                  # 'alternate_contact_no', 'alternate_email', 'street', 'zip_code',
                  'city', 'country', 'role',
                  'category', 'added_by', 'registration_date', 'delete']
        attrs = {'class': 'table table-sm'}
        order_by = ("-registration_date",)


class ActivityTable(tables.Table):
    """
    activity table to view activity performed by company admin in portal
    """

    class Meta:
        model = ActivityMonitor
        fields = ['id', 'performed_by', 'activity_type', 'affected_user', 'bulk_create', 'status', 'time_stamp',
                  'remarks']
        attrs = {'class': 'table table-sm'}
        order_by = ("-time_stamp",)


class SurveyTable(tables.Table):
    """ survey table to view/manage surveys """
    id = tables.TemplateColumn("""
        <a style="text-decoration:None" href="{% url 'create_survey' survey_id=record.id step=record.steps %}">{{record.id}}</a>""")
    steps = tables.TemplateColumn("""
        <ul class="survey-progress">
            {% load custom_tags %}
            {% for i in 0|filter_range:record.steps %}
                <li class="survey-form-complete"></li>
            {% endfor %}
            {% for j in record.steps|filter_range:5 %}
                <li class="survey-form-incomplete"></li>
            {% endfor %}
        </ul>
        """)
    edit = tables.TemplateColumn("""{% load static %}
        <a style="text-decoration:None" href="{% url 'create_survey' survey_id=record.id step=record.steps %}">
        <img src="{% static '/assets/images/editicon.png' %}" width="25px" /></a>
    """)
    delete = tables.TemplateColumn("""{% load static %}
        <form action="{% url 'delete_survey' pk=record.id %}" method="POST"> {% csrf_token %}
            <input class="btn btn-default btn-danger" type="submit" value="Delete">            </input>
        </form>""", orderable=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'question', 'date_created', 'employee_group', 'steps',
                  'edit', 'start_date', 'delete']
        attrs = {'class': 'table survey-table table-responsive'}
        order_by = ("-time_stamp",)


class NewsFeedTable(tables.Table):
    """ survey table to view/manage surveys """
    id = tables.TemplateColumn("""
        <a style="text-decoration:None" href="#">{{record.id}}</a>""")
    delete = tables.TemplateColumn("""{% load static %}
            <form action="{% url 'delete_news_feed' pk=record.id %}" method="POST"> {% csrf_token %}
                <input class="btn btn-default btn-danger" type="submit" value="Delete">            </input>
            </form>""", orderable=False)

    class Meta:
        model = NewsFeed
        fields = ['id', 'title', 'feed', 'date_created', 'delete']
        attrs = {'class': 'table survey-table table-responsive'}
        order_by = ("-date_created",)
