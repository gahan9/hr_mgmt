import os
import random

import time
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone
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
    # flag = False
    if flag:
        time.sleep(seconds)


class LoginTest(TestCase):
    fixtures = ['data_dump.json']
    hr_credentials = {"contact_number": '+919999999901', "password": computeMD5hash('1')}
    user_credentials = {"contact_number": '+919999999902', "password": computeMD5hash('1')}

    def test_hr_login(self):
        self.client.login(**self.hr_credentials)  # login to the system
        response = self.client.get(reverse_lazy('home'), follow=True)  # try to access home page
        self.assertFalse(response.context['user'].is_anonymous, "User unable to log in with given credentials")
        self.assertTrue(response.context['user'].is_hr, "Logged in User is not HR")
        self.client.get(reverse_lazy('logout'))

    def test_user_login(self):
        self.client.login(**self.user_credentials)
        response = self.client.get(reverse_lazy('home'), follow=True)
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertTrue(response.context['user'].is_employee)
        self.client.get(reverse_lazy('logout'))


class BaseLoginTest(StaticLiveServerTestCase):
    fixtures = None
    user_credentials = {"username": '+919999999902', "password": '1'}

    def take_snapshot(self):
        _sleep(1)
        _name = "snapshot_{}.png".format(timezone.now().strftime('%Y-%d-%m_%H.%M.%S'))
        _path = os.path.join(getattr(settings, 'MEDIA_ROOT'), 'selenium', _name)
        self.selenium.save_screenshot(_path)
        print("Snapshot saved at: {}".format(_path))

    def setup_incognito(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.DEBUG = True
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(15)
        # cls.driver.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

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

    def generate_profile(self, gender="M", role=3):
        if gender == "F":
            _first_name, _last_name = faker.name_female().split()
        else:
            _first_name, _last_name = faker.name_male().split()
        return {
            "contact_number": self.get_phone_number(),
            "profile_image": self.get_profile_image(),
            "role": 3,
            "first_name": _first_name,
            "last_name": _last_name,
            "email": faker.email(),
            "password": faker.password(),
            "gender": gender,
        }

    def generate_employee_profile(self):
        return {
            "job_title": faker.job(),
            "street": faker.street_address(),
            "zip_code": faker.zipcode(),
            "city": faker.city(),
            "country": faker.country(),
            "category": faker.country(),
        }

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

    def _login(self, **kwargs):
        """
        login to system with credential created
        :param kwargs:
            : credentials: provide credentials for login
            : driver: provide web driver if not self.selenium used in setup
        :return:
        """
        driver = kwargs.get('driver', self.selenium)
        credentials = kwargs.get('credentials', self.user_credentials)
        driver.get(self.login_url)  # /login/
        _username = credentials['username']
        _password = credentials['password']
        username_input = driver.find_element_by_name("username")
        username_input.send_keys(_username)
        password_input = driver.find_element_by_name("password")
        password_input.send_keys(_password)
        driver.find_element_by_id('login').click()

    def _logout(self):
        self.selenium.get("{}{}".format(self.live_server_url, reverse_lazy('logout')))

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
        cred = {"username": self.contact_number, "password": self.password}
        self._login(credentials=cred)
        self.common_test_after_login()
        _sleep(5)


class LoginTestWithFixture(BaseLoginTest):
    fixtures = ['mf.json']

    def test_ordered_with_fixtures(self):
        #  load fixtures before running this test
        cred = {"username": self.contact_number, "password": self.password}
        self._login(credentials=cred)
        self.common_test_after_login()
        self._logout()
        _sleep(5)

    def test_modify_employee_data(self):
        self._test_login(flag=True)
        self.take_snapshot()
        self._click_link('employee_data')
        self._click_link('view_data')  # reached at view employee data
        self.take_snapshot()
        cred = {"username": "+919999999904", "password": "r@123456789"}
        self.selenium.find_element_by_link_text(cred['username']).click()  # select employee by number
        _field = self.selenium.find_element_by_name('email')  # select field
        self.take_snapshot()
        _field.clear()  # clear field
        _field.send_keys(faker.company_email())  # enter random email
        self.take_snapshot()
        self.selenium.find_element_by_xpath("//input[contains(@type, 'submit')]").click()
        self.selenium.find_element_by_link_text(cred['username']).click()
        self.take_snapshot()
        self.selenium.find_element_by_partial_link_text("Reset Password").click()
        _password = self.selenium.find_element_by_name('password')  # select password element
        self.take_snapshot()
        _password.clear()  # clear password
        _password.send_keys(cred['password'])  # enter password
        self.take_snapshot()
        self.selenium.find_element_by_xpath("//input[contains(@type, 'submit')]").click()
        self.take_snapshot()
        self._logout()
        self.take_snapshot()
        self._login(credentials=cred)
        self.take_snapshot()
        self._logout()
        # self.incognito_login(flag=True)
