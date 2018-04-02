import random

import time
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse_lazy
from selenium import webdriver

from employee.models import Employee
from main.models import Company, ActivityMonitor, Plan
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
        self.number = random.randint(7000000000, 9999999999)
        self.first_name, self.last_name = faker.name().split()
        self.email = faker.email()
        self.company_name = faker.company()
        self.country_code = faker.country_code()
        self.name_length = None
        self.company_postfix = ['Co', 'Organization', 'Ltd.', 'Corporation', 'Management']

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


class LoginTest(StaticLiveServerTestCase):
    # fixtures = ['data_dump.json']

    def setUp(self):
        self.credentials = {
            "username": '+919999999901',
            "password": '1'
        }
        self.number = random.randint(7700000000, 9999999999)
        self.first_name, self.last_name = faker.name().split()
        self.email = faker.email()
        self.company_name = faker.company()
        self.country_code = faker.country_code()
        self.password = "r@123456"
        self.name_length = None
        self.company_postfix = ['Co', 'Organization', 'Ltd.', 'Corporation', 'Management']

    def _create_plan(self):
        # test demo create plan by admin
        Plan.objects.create(plan_name=1, plan_price=49)

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

    def _test_purchase_plan(self):
        _url = "{}{}".format(self.live_server_url, reverse_lazy('select_plan'))
        self.selenium.get(_url)
        contact_number_input = self.selenium.find_element_by_name('contact_number')
        contact_number_input.send_keys("+91{}".format(self.number))
        first_name_input = self.selenium.find_element_by_name('first_name')
        first_name_input.send_keys(self.first_name)
        last_name_input = self.selenium.find_element_by_name('last_name')
        last_name_input.send_keys(self.last_name)
        email_input = self.selenium.find_element_by_name('email')
        email_input.send_keys(self.email)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(self.password)
        self.selenium.find_element_by_name('submit').click()
        time.sleep(3)

    def _test_login(self):
        _url = "{}{}".format(self.live_server_url, reverse_lazy('login'))
        self.selenium.get(_url)
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("+91{}".format(self.number))
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(self.password)
        self.selenium.find_element_by_id('login').click()
        time.sleep(5)

    def test_ordered(self):
        self._create_plan()
        self._test_purchase_plan()
        self._test_login()
