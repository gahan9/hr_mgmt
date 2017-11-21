from main.models import *
import django_tables2 as tables
from employee.models import *


class EmployeeTable(tables.Table):
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    email = tables.Column(accessor='user.email', verbose_name='Email Address')

    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'contact_no', 'email', 'alternate_email',
                  'alternate_contact_no', 'job_title', 'street', 'zip_code', 'city', 'country',
                  'registration_date']
        attrs = {'class': 'table table-sm'}
        order_by = ("-registration_date",)
