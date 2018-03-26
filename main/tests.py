import random

import time
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from employee.models import Employee
from main.models import Company, ActivityMonitor
from main.utility import set_password_hash
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver

User = get_user_model()


class DashboardTest(TestCase):
    fixtures = ['dump.json']
    def setUpTestData(self):
        self.number = random.randint(1000000000, 9999999999)
        self.name = self.random_name()
        self.email = self.random_email()
        self.company_name = self.random_company_name()
        self.name_length = None
        self.company_postfix = ['Co', 'Organization', 'Ltd.', 'Corporation', 'Management']

    def random_name(self, _name_length=random.randint(3, 20)):
        name_length = self.name_length if self.name_length else _name_length
        _name = ''.join([chr(random.choice(range(97, 122))) for i in range(name_length)])
        return _name

    def random_email(self):
        _email = "{}@{}.com".format(self.random_name(), self.random_name())
        return _email

    def random_company_name(self):
        _company = "{} {}".format(self.random_name(), random.choice(self.company_postfix))
        return _company

    def test_create_hr(self):
        _hr = User.objects.create(contact_number=self.number, email=self.email,
                                  first_name=self.name, last_name=self.name,
                                  password=set_password_hash(self.number), role=2)
        _activity_instance = ActivityMonitor.objects.create(
            activity_type=0, performed_by=self.performer, affected_user=_hr)
        _company_instance = Company.objects.create(company_user=_hr,
                                                   name=self.company_name,
                                                   alternate_contact_no=random.randint(1000000000, 9999999999),
                                                   alternate_email=self.email,
                                                   country='US')

    def test_create_employee(self):
        _main_profile = User.objects.create(contact_number=self.number, email=self.email,
                                        first_name=self.name, last_name=self.name,
                                        password=set_password_hash(self.number), role=3)
        _activity_instance = ActivityMonitor.objects.create(
            activity_type=0, performed_by=self.performer, affected_user=_main_profile)
        _employee = Employee.objects.create(user=_main_profile,
                                            company_name=self.company,
                                            job_title='job_title',
                                            alternate_email=self.email,
                                            alternate_contact_no=self.number, street='street',
                                            zip_code=random.randint(10000, 99999),
                                            city='city', country='US')


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['auth.json']

    def setUp(self):
        settings.DEBUG = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('8888888802')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1')
        self.selenium.find_element_by_id('login').click()
        time.sleep(30)
