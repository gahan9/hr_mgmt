import django_tables2 as tables
from employee.models import *


class EmployeeTable(tables.Table):
    # id = tables.LinkColumn('employee:edit_data', args=[Employee('pk')])
    id = tables.TemplateColumn('<a href="/edit_data/{{record.id}}">{{record.id}}</a>')
    # contact_number = tables.Column(accessor='user.contact_number', verbose_name='Mobile Number')
    contact_number = tables.TemplateColumn(accessor='user.contact_number', template_code='<a href="/edit_data/{{record.id}}">{{record.user.contact_number}}</a>')
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    email = tables.Column(accessor='user.email', verbose_name='Email Address')
    role = tables.Column(accessor='user.role', verbose_name='Role')
    category = tables.Column(verbose_name='Region')
    added_by = tables.Column(verbose_name='Created by')

    class Meta:
        model = Employee
        fields = ['id', 'contact_number', 'first_name', 'last_name', 'email', 'alternate_email',
                  'alternate_contact_no', 'job_title', 'street', 'zip_code', 'city', 'country', 'role',
                  'category', 'added_by', 'registration_date']
        attrs = {'class': 'table table-sm'}
        order_by = ("-registration_date",)
