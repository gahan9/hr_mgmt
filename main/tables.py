from .models import *
import django_tables2 as tables


class EmployeeDataTable(tables.Table):
    first_name = tables.Column(accessor='user.first_name', verbose_name='First Name')
    last_name = tables.Column(accessor='user.last_name', verbose_name='Last Name')
    email = tables.Column(accessor='user.email', verbose_name='Email Address')

    class Meta:
        model = EmployeeData
        fields = ['id', 'first_name', 'last_name', 'contact_no', 'email', 'registration_date']
        attrs = {'class': 'table table-sm'}
        order_by = ("-registration_date",)
