import os
import random

import time
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse_lazy
from selenium import webdriver
from selenium.webdriver.support.select import Select

from employee.models import Employee
from main.models import Company, ActivityMonitor, Plan
from main.utility import set_password_hash, computeMD5hash
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.chrome.webdriver import WebDriver
from faker import Faker
User = get_user_model()

faker = Faker()


def _sleep(seconds=2, flag=True):
    flag = False
    if flag:
        time.sleep(seconds)


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


class BaseLoginTest(StaticLiveServerTestCase):
    fixtures = None

    def setUp(self):
        self.credentials = {
            "username": '+919999999901',
            "password": '1'
        }
        self.login_url = "{}{}".format(self.live_server_url, reverse_lazy('login'))
        self.country_code = "+91"
        self.number = random.randint(7700000000, 9999999999)
        self.contact_number = "{}{}".format(self.country_code, self.number)
        self.first_name, self.last_name = faker.name().split()
        self.email = faker.email()
        self.company_name = faker.company()
        self.country_code = faker.country_code()
        self.password = "r@123456"
        self.name_length = None
        self.company_postfix = ['Co', 'Organization', 'Ltd.', 'Corporation', 'Management']
        self.path = '/home/quixom/Pictures/Wallpapers/'

    def get_profile_image(self):
        if os.path.exists(self.path):
            images = os.listdir(self.path)
            return os.path.join(self.path, random.choice(images))
        else:
            return None

    def get_phone_number(self):
        return "+91{}".format(random.randint(7700000000, 9999999999))

    def _create_plan(self):
        # test demo create plan by admin
        Plan.objects.create(plan_name=1, plan_price=49)
        Plan.objects.create(plan_name=1, plan_price=4.99)

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
        # creates dashboard account - HR user creation
        _url = "{}{}".format(self.live_server_url, reverse_lazy('select_plan'))
        self.selenium.get(_url)  # /select-plan/
        # input fields to be fill form
        input_fields = ['contact_number', 'first_name', 'last_name', 'email', 'password']
        for field in input_fields:
            # fill the form with input fields set up in setUp class
            self.selenium.find_element_by_name(field).send_keys(getattr(self, field))
        gender_select = Select(self.selenium.find_element_by_name('gender'))
        gender_select.select_by_visible_text('Male')
        plan_select = Select(self.selenium.find_element_by_name('has_plan'))
        plan_select.select_by_value("1")
        self.selenium.find_element_by_name('submit').click()
        _sleep(1)

    def _test_login(self, **kwargs):
        # login to system with credential created
        self.selenium.get(self.login_url)  # /login/
        flag = kwargs.get('flag', True)
        if flag:
            _username = self.credentials['username']
            _password = self.credentials['password']
        else:
            _username = self.contact_number
            _password = self.password
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(_username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(_password)
        self.selenium.find_element_by_id('login').click()

    def _click_link(self, link_href='view_data'):
        self.selenium.find_element_by_xpath("//a[contains(@href,'{}')]".format(link_href)).click()
        _sleep(2)

    def _create_user(self, gender="M"):
        self.selenium.find_element_by_name('contact_number').send_keys(self.get_phone_number())
        self.selenium.find_element_by_name('profile_image').send_keys(self.get_profile_image())
        if gender == "F":
            _first_name, _last_name = faker.name_female().split()
            _gender = "Female"
        else:
            _first_name, _last_name = faker.name_male().split()
            _gender = "Male"
        self.selenium.find_element_by_name('first_name').send_keys(_first_name)
        self.selenium.find_element_by_name('last_name').send_keys(_last_name)
        self.selenium.find_element_by_name('email').send_keys(faker.email())
        self.selenium.find_element_by_name('password').send_keys(faker.password())
        self.selenium.find_element_by_name('job_title').send_keys(faker.job())
        self.selenium.find_element_by_name('street').send_keys(faker.street_address())
        self.selenium.find_element_by_name('zip_code').send_keys(faker.zipcode())
        self.selenium.find_element_by_name('city').send_keys(faker.city())
        self.selenium.find_element_by_name('country').send_keys(faker.country())
        Select(self.selenium.find_element_by_name('role')).select_by_visible_text('Employee')
        Select(self.selenium.find_element_by_name('gender')).select_by_visible_text(_gender)
        self.selenium.find_element_by_xpath("//input[contains(@type, 'submit')]").click()
        _sleep(5)

    def common_test_after_login(self):
        self._click_link('employee_data')
        self._click_link('view_data')
        self.selenium.back()
        self.selenium.back()
        self._click_link('settings')
        self._click_link('create_user')
        self._create_user()
        self.selenium.get("{}{}".format(self.live_server_url, reverse_lazy('view_data')))


class LoginTestWithoutFixture(BaseLoginTest):
    def test_ordered(self):
        # test method to execute tests in order
        self._create_plan()
        self._test_purchase_plan()
        self._test_login(flag=False)
        self.common_test_after_login()
        _sleep(5)


class LoginTestWithFixture(BaseLoginTest):
    fixtures = ['data_dump.json']

    def test_ordered_with_fixtures(self):
        #  load fixtures before running this test
        self._test_login(flag=True)
        self.common_test_after_login()
        self.selenium.get("{}{}".format(self.live_server_url, reverse_lazy('logout')))
        _sleep(5)
