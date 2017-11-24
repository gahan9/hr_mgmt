from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from employee.models import Employee, Company
from main.models import ActivityMonitor
import random

UserModel = get_user_model()


def create_demo():
    number = random.randint(1000000000, 9999999999)
    name = "demo"
    email = "{0}@{0}.{0}".format(number)
    performer = UserModel.objects.get(id=7)
    company = Company.objects.get(id=2)
    user_obj = UserModel.objects.create(contact_number=number, email=email, first_name=name, last_name=name,
                                        password=make_password(number), role=3, )

    ActivityMonitor.objects.create(activity_type=0, performed_by=performer, affected_user=user_obj)
    Employee.objects.create(user=user_obj, company_name=company, job_title='job_title', alternate_email=email,
                            alternate_contact_no=number, street='street', zip_code=random.randint(10000, 99999),
                            city='city', country='US')
