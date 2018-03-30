import random

import time
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse_lazy
from selenium import webdriver

from employee.models import Employee
from main.models import Company, ActivityMonitor
from main.utility import set_password_hash, computeMD5hash
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from faker import Faker
User = get_user_model()

faker = Faker()


class LoginTest(TestCase):
    fixtures = ['data_dump.json']
    hr_credentials = {"contact_number": '9999999901', "password": computeMD5hash('1')}
    user_credentials = {"contact_number": '8888888808', "password": computeMD5hash('1')}

    def test_hr_login(self):
        self.client.login(**self.hr_credentials)  # login to the system
        response = self.client.get(reverse_lazy('home'), follow=True)  # try to access home page
        self.assertFalse(response.context['user'].is_anonymous, "User unable to log in with given credentials")
        self.assertTrue(response.context['user'].is_hr, "Logged in User is not HR")

    def test_user_login(self):
        self.client.login(**self.user_credentials)
        response = self.client.get(reverse_lazy('home'), follow=True)
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertTrue(response.context['user'].is_employee)


class DashboardTest(TestCase):
    # fixtures = ['dump.json']

    def setUpTestData(self):
        self.number = random.randint(1000000000, 9999999999)
        self.first_name, self.last_name = faker.name().split()
        self.email = faker.email()
        self.company_name = faker.company()
        self.country_code = faker.country_code()
        self.name_length = None
        self.company_postfix = ['Co', 'Organization', 'Ltd.', 'Corporation', 'Management']

    def random_name(self, _name_length=random.randint(3, 20)):
        name_length = self.name_length if self.name_length else _name_length
        _name = ''.join([chr(random.choice(range(97, 122))) for i in range(name_length)])
        return _name

    def old_test_create_hr(self):
        _hr = User.objects.create(contact_number=self.number, email=self.email,
                                  first_name=self.first_name, last_name=self.last_name,
                                  password=set_password_hash(self.number), role=2)
        _activity_instance = ActivityMonitor.objects.create(
            activity_type=0, performed_by=_hr, affected_user=_hr)
        _company_instance = Company.objects.create(company_user=_hr,
                                                   name=self.company_name,
                                                   alternate_contact_no=random.randint(1000000000, 9999999999),
                                                   alternate_email=self.email,
                                                   country=self.country_code)

    def old_test_create_employee(self):
        _main_profile = User.objects.create(contact_number=self.number, email=self.email,
                                            first_name=self.first_name, last_name=self.last_name,
                                            password=set_password_hash(self.number), role=3)
        _activity_instance = ActivityMonitor.objects.create(
            activity_type=0, performed_by=_main_profile, affected_user=_main_profile)
        _employee = Employee.objects.create(user=_main_profile,
                                            company_name=self.company_name,
                                            job_title='job_title',
                                            alternate_email=self.email,
                                            alternate_contact_no=self.number, street='street',
                                            zip_code=random.randint(10000, 99999),
                                            city='city', country='US')


class MySeleniumTests(StaticLiveServerTestCase):
    fixtures = ['data_dump.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.DEBUG = True
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('9999999901')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('1')
        self.selenium.find_element_by_id('login').click()
        time.sleep(5)
