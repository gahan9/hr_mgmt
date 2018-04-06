from unittest import skipIf, skip

from django.test import TestCase, tag
import random
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from django.contrib.auth.hashers import make_password

from employee.models import *
from main.models import *
from main.tests import _sleep, generate_dump
from main.utility import computeMD5hash, set_password_hash


class DRFTest(APITestCase):
    # fixtures = generate_dump()
    fixtures = ['employee.json', 'fileupload.json', 'newsfeed.json', 'questiondb.json', 'survey.json', 'surveyresponse.json', 'company.json', 'usermodel.json', 'plan.json', 'activitymonitor.json']
    user_credentials = {"username": "+919999999902", "password": computeMD5hash('1')}

    def setUp(self):
        key = self._get_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)

    def _get_token(self, contact_number=None):
        contact_number = contact_number if contact_number else self.user_credentials["username"]
        token, created = Token.objects.get_or_create(user=UserModel.objects.get(contact_number=contact_number))
        return token.key

    def _authorize_token(self, key):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + key)

    def _regenerate_fixture(self):
        self.fixtures = generate_dump()

    @tag('fast', 'core', 'employee')
    def test_get_auth_token(self):
        """ Employee authentication API """
        url = reverse_lazy('get_auth_token')
        payload = self.user_credentials
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "invalid payload/credential")
        _user = UserModel.objects.get(contact_number=payload.get('username'))
        self.assertEqual(response.data['token'], self._get_token(payload.get('username')), "Token mismatch")
        self.assertEqual(response.data['id'], _user.id, "User ID mismatch")
        self.assertEqual(response.data['role'], 3, "User is not employee")
        self.assertEqual(response.data['hr_id'], _user.employee.added_by.id, "HR ID mismatch")

    @skipIf(True, "I don't want to run this test yet")
    @tag('slow', 'hr')
    def test_create_question(self):
        """
        Ensure we can create a new question object.
        """
        url = reverse_lazy('questiondb-list')
        payload = {'question': 'How is this...?'}
        token, created = Token.objects.get_or_create(user=UserModel.objects.get(contact_number='+919999999901'))
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        _existing_questions = QuestionDB.objects.count()
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "status code mismatch")
        self.assertEqual(QuestionDB.objects.count(), _existing_questions+1, "Total question count not matched")
        self.assertEqual(QuestionDB.objects.last().question, payload.get('question'), "Question title does not match")


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
