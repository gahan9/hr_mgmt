from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from employee.models import Employee, Company
from main.models import ActivityMonitor
import random

from main.utility import computeMD5hash

UserModel = get_user_model()


def change_all_password():
    UserModel.objects.filter(is_staff=False).update(password=make_password(computeMD5hash('1')))


def dummy_employee(role=3):
    """
    test case to create user followed by it's employee detail
    :param role:
    :return:
    """
    number = random.randint(1000000000, 9999999999)
    name = "demo"
    email = "{0}@{0}.{0}".format(number)
    performer = UserModel.objects.get(id=7)
    company = Company.objects.get(id=2)
    user_obj = UserModel.objects.create(contact_number=number, email=email, first_name=name, last_name=name,
                                        password=make_password(computeMD5hash(number)), role=role, )

    ActivityMonitor.objects.create(company_id=company.id, activity_type=0, performed_by=performer.get_detail(), affected_user=user_obj.get_detail())
    Employee.objects.create(user=user_obj, company_name=company, job_title='job_title', alternate_email=email,
                            alternate_contact_no=number, street='street', zip_code=random.randint(10000, 99999),
                            city='city', country='US')
