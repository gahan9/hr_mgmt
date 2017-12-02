from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.files.storage import FileSystemStorage
from django.db import models
from django_countries.fields import CountryField
from rest_framework.fields import JSONField

from employee_management import settings

fs = FileSystemStorage(location='/var/www/html/field_rate/photos')


class MyUserManager(UserManager):
    def create_user(self, contact_number, password=None, **kwargs):
        """
        Creates and saves a User with the given contact_number and password.
        """
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

    def create_superuser(self, contact_number, password, **kwargs):
        """
        Creates and saves a superuser with the given contact_number and password.
        """
        u = self.create_user(contact_number, password=password, is_hr=True, is_head_hr=True)
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


class UserModel(AbstractUser):
    ROLE_CHOICES = (
        (1, 'Head HR'),
        (2, 'HR'),
        (3, 'Employee')
    )
    contact_number = models.CharField(max_length=12, unique=True, verbose_name="Contact Number")
    profile_image = models.ImageField(storage=fs, blank=True, null=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=3)
    username = models.CharField(max_length=10, blank=True, null=True, unique=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'contact_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_detail(self):
        return {'number': self.contact_number, 'first_name': self.first_name, 'last_name': self.last_name, 'role': self.role}

    def __str__(self):
        return "{}- {}".format(self.contact_number, self.first_name)


class Company(models.Model):
    company_user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='rel_company_user')
    name = models.CharField(max_length=100, verbose_name="Company Name", unique=True)
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True,
                                            verbose_name="Alternate Contact Number")
    alternate_email = models.EmailField(blank=True, null=True, verbose_name="Alternate Email")
    country = models.CharField(max_length=50, verbose_name="Country", blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"


class FileUpload(models.Model):
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    file = models.FileField(upload_to='.', verbose_name="File")
    added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.file)

    class Meta:
        verbose_name_plural = "Uploads"


class ActivityMonitor(models.Model):
    company = models.ForeignKey(Company)
    activity_type = models.IntegerField(choices=[(0, 'create'), (1, 'change'), (2, 'delete')])
    performed_by = models.TextField(null=True, blank=True)
    affected_user = models.TextField(null=True, blank=True)
    bulk_create = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Activity Monitor"
