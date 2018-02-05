import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from djmoney.models.fields import MoneyField

from employee_management import settings

import firebase_admin
from firebase_admin import auth, credentials
from employee_management.settings import FIREBASE_CREDENTIAL_JSON

fs = FileSystemStorage(location='/var/www/html/field_rate/photos')


class MyUserManager(UserManager):
    def create_user(self, contact_number, password=None, **kwargs):
        """ Creates and saves a User with the given contact_number and password. """
        if not contact_number:
            raise ValueError('Users must have an contact number')
        user = self.model(contact_number=contact_number)
        user.set_password(password)
        if "first_name" in kwargs.keys():
            user.first_name = kwargs['first_name']
        if "last_name" in kwargs.keys():
            user.last_name = kwargs['last_name']
        user.save(using=self._db)
        return user

    def create_superuser(self, contact_number, password, email, **kwargs):
        """ Creates and saves a superuser with the given contact_number and password. """
        u = self.create_user(contact_number, password=password, email=email)
        u.is_admin = True
        u.is_staff = True
        u.is_superuser = True
        u.role = 1  # Head HR
        if "first_name" in kwargs.keys():
            u.first_name = kwargs['first_name']
        if "last_name" in kwargs.keys():
            u.last_name = kwargs['last_name']
        u.save(using=self._db)
        return u


class Plan(models.Model):
    CHOICES = [(1, "Individual"), (2, "Company")]
    plan_name = models.IntegerField(
        choices=CHOICES, default=2,
        verbose_name="Select subscription type",
        help_text="select if subscription is for individual or company")
    plan_price = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    plan_validity = models.IntegerField(default=180, help_text="Days after plan expires")  # plan validity days

    def get_price(self):
        return "{} {}".format(self.plan_price.currency, self.plan_price.amount)

    def get_plan_details(self):
        return {'name': self.get_plan_name_display(), 'price': self.get_price(),
                'period': "{} days".format(self.plan_validity)}

    def __str__(self):
        return "{}".format(self.get_plan_details())

    @property
    def is_taken_company(self):
        return True if self.plan_name == 2 else False

    @property
    def is_taken_hr_plan(self):
        return True if self.plan_name == 1 else False


class UserModel(AbstractUser):
    """
    Custom User model extends AbstractUser to user contact number and password for login
    """
    ROLE_CHOICES = (
        (1, 'Owner'),
        (2, 'HR'),
        (3, 'Employee')
    )
    contact_number = models.CharField(max_length=12, unique=True, verbose_name="Contact Number")
    profile_image = models.ImageField(upload_to='media/uploads/', blank=True, null=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=3)
    username = models.CharField(max_length=10, blank=True, null=True, unique=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Account Suspended", help_text="account is disabled by HR")
    has_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    # remark = models.TextField(blank=True, null=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'contact_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def get_detail(self):
        """
        :return: details of current user model
        """
        return {'id': self.id, 'number': self.contact_number, 'first_name': self.first_name, 'last_name': self.last_name, 'role': self.role}

    def __str__(self):
        return "{}- {}".format(self.contact_number, self.first_name)


class Company(models.Model):
    """
    Company Model created by Super User
    """
    company_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rel_company_user')
    name = models.CharField(max_length=100, verbose_name="Company Name", blank=True, null=True)
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True,
                                            verbose_name="Alternate Contact Number")
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    country = models.CharField(max_length=50, verbose_name="Country", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    subscription_expired = models.BooleanField(default=False)
    region = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class ActivityMonitor(models.Model):
    """ Model to store activity performed by company admin (HR) """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    activity_type = models.IntegerField(choices=[(0, 'create'), (1, 'change'), (2, 'delete')])
    performed_by = models.TextField(null=True, blank=True)
    affected_user = models.TextField(null=True, blank=True)
    bulk_create = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Activity Monitor"


# method for creating user in firebase
@receiver(post_save, sender=UserModel, dispatch_uid="create_firebase_account")
def create_firebase_account(sender, instance, created, *args, **kwargs):
    HOST = "http://{}:8889".format(os.popen('hostname -I').read().strip())
    print("In create firebase account")
    data = {}
    country_code = "+91"
    data['uid'] = str(instance.id)
    if instance.first_name:
        data['display_name'] = instance.first_name
    if instance.email:
        data['email'] = instance.email
    if instance.profile_image:
        data['photo_url'] = "{}{}".format(HOST, instance.profile_image)
    data['password'] = "{}@{}".format(instance.first_name, instance.contact_number)
    data['phone_number'] = "{}{}".format(country_code, instance.contact_number)
    print("post_save : signal", sender, instance, created, kwargs, args)
    try:
        DEFAULT_APP = firebase_admin.initialize_app(credentials.Certificate(FIREBASE_CREDENTIAL_JSON))
    except ValueError:
        print("app already exist....")
        pass
    if created:
        user_create_response = auth.create_user(**data)
        print(user_create_response)
