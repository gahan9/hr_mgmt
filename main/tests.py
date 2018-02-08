import random

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from employee.models import Employee
from main.models import Company, ActivityMonitor
from main.utility import computeMD5hash

UserModel = get_user_model()


# Create company


class Test(object):
    def __init__(self, *args, **kwargs):
        self.number = random.randint(1000000000, 9999999999)
        self.name = "demo"
        self.email = "{0}@{0}.{0}".format(self.number)
        self.performer = UserModel.objects.get(id=7)
        self.company = Company.objects.get(id=2)
        self.company_name = "dummy company"

    def dummy_employee(self, role=3):
        user_obj = UserModel.objects.create(contact_number=self.number, email=self.email,
                                            first_name=self.name, last_name=self.name,
                                            password=make_password(computeMD5hash(self.number)), role=role, )

        ActivityMonitor.objects.create(activity_type=0, performed_by=self.performer,
                                       affected_user=user_obj)
        Employee.objects.create(user=user_obj, company_name=self.company,
                                job_title='job_title',
                                alternate_email=self.email,
                                alternate_contact_no=self.number, street='street',
                                zip_code=random.randint(10000, 99999),
                                city='city', country='US')

    def dummy_company(self, role=1):
        user_obj = UserModel.objects.create(contact_number=self.number, email=self.email,
                                            first_name=self.name, last_name=self.name,
                                            password=make_password(computeMD5hash(self.number)),
                                            role=role,
                                            )
        company_obj = Company.objects.create(company_user=user_obj, name=self.company_name,
                                             alternate_contact_no=random.randint(1000000000, 9999999999),
                                             alternate_email=self.email,
                                             country='US')


if __name__ == "__main__":
    t = Test()
    t.dummy_employee()