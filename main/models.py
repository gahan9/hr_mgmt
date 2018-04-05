from django.contrib.auth.models import AbstractUser, UserManager
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from rest_framework.authtoken.models import Token

from djmoney.models.fields import MoneyField

from employee_management import settings


class MyUserManager(UserManager):
    def create_user(self, contact_number, password=None, **kwargs):
        """ Creates and saves a User with the given contact_number and password. """
        if not contact_number:
            raise ValueError('Users must have an contact number')
        user = self.model(contact_number=contact_number)
        user.set_password(password)
        user.first_name = kwargs.get('first_name', None)
        user.last_name = kwargs.get('last_name', None)
        user.save(using=self._db)
        return user

    def create_superuser(self, contact_number, password, email, **kwargs):
        """ Creates and saves a superuser with the given contact_number and password. """
        u = self.create_user(contact_number, password=password, email=email, **kwargs)
        u.is_admin = True
        u.is_staff = True
        u.is_superuser = True
        u.role = 1  # Head HR
        u.first_name = kwargs.get('first_name', None)
        u.last_name = kwargs.get('last_name', None)
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

    @property
    def get_price(self):
        return "{} {}".format(self.plan_price.currency, self.plan_price.amount)

    @property
    def get_plan_details(self):
        return model_to_dict(self)

    def __str__(self):
        return "{}".format(self.get_plan_details)

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
    GENDER_CHOICE = (
        ('M', 'Male'),
        ('F', 'Female'),
        # ('O', 'Other')
    )
    # contact_number = models.CharField(max_length=12, unique=True, verbose_name="Contact Number")
    contact_number = PhoneNumberField(unique=True,
                                      verbose_name=_("Contact Number"),
                                      help_text=_("Contact Number with country code"))
    profile_image = models.ImageField(upload_to='media/uploads/', blank=True, null=True,
                                      verbose_name=_("Profile Image"),
                                      help_text=_("Profile Picture"))
    role = models.IntegerField(choices=ROLE_CHOICES, default=3,
                               verbose_name=_("Role of user"),
                               help_text=_("User Role in system"))  # (2 - HR; 3 - Employee)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE, default='M')
    username = models.CharField(max_length=10, blank=True, null=True, unique=False)
    is_blocked = models.BooleanField(default=False,
                                     verbose_name=_("Account Suspended"),
                                     help_text=_("account is disabled by HR"))
    has_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True,
                                             verbose_name=_("Registration Date of User"),
                                             help_text=_("Registration Date of User"))
    date_updated = models.DateTimeField(auto_now=True)
    # remark = models.TextField(blank=True, null=True)

    objects = MyUserManager()
    USERNAME_FIELD = 'contact_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    @property
    def profile_image_url(self):
        if self.has_profile_image:
            # returns url of profile image
            return self.profile_image.url
        else:
            # if user didn't set any profile image then return dummy image
            return "http://lorempixel.com/300/300/"

    @property
    def has_profile_image(self):
        return bool(self.profile_image)

    @property
    def has_subscription(self):
        return bool(self.has_plan)

    @property
    def subscribed_since(self):
        _now = timezone.now()
        if self.is_hr:
            return _now - self.registration_date
        elif hasattr(self, 'employee'):
            return _now - self.employee.added_by.registration_date
        else:
            return False

    @property
    def get_plan_validity(self):
        return self.has_plan

    @property
    def has_active_subscription(self):
        if self.has_subscription:
            if self.is_hr or hasattr(self, 'employee'):
                if self.subscribed_since:
                    return bool(self.has_plan.plan_validity >= self.subscribed_since)
            else:
                return False
        else:
            return False

    @property
    def is_employee(self):
        return bool(self.role <= 3 and hasattr(self, 'employee'))

    @property
    def is_hr(self):
        return bool(self.role <= 2)

    @property
    def is_owner(self):
        return bool(self.role <= 1)

    @property
    def get_creator(self):
        if hasattr(self, 'employee'):
            # get details of creator (HR) if user is employee
            _record_creator = self.employee.added_by
            return {
                'hr_id': _record_creator.id,
                'hr_name': _record_creator.first_name,
                'hr_profile_image': _record_creator.profile_image.url if _record_creator.profile_image else None,
            }
        else:
            return model_to_dict(self)

    @property
    def get_auth_token(self):
        token, created = Token.objects.get_or_create(user=self)
        return token

    def get_detail(self):
        """
        :return: details of current user model
        """
        return {'id': self.id, 'contact_number': self.contact_number, 'first_name': self.first_name, 'last_name': self.last_name, 'role': self.role}

    @property
    def detail(self):
        """
        :return: details of current user model
        """
        return {
            'id'            : self.id,
            'contact_number': self.contact_number.as_e164,
            'first_name'    : self.first_name,
            'last_name'     : self.last_name,
            'role'          : self.role
        }

    def __str__(self):
        return "{}- {}".format(self.contact_number.as_e164, self.first_name)


class Company(models.Model):
    """
    Company Model created by Super User
    """
    company_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                        related_name='rel_company_user',
                                        help_text=_("Foreign Key to User(HR) who purchased Plan"))
    name = models.CharField(max_length=100, blank=True, null=True,
                            verbose_name=_("Company Name"),
                            help_text=_("Name of Company"))
    alternate_contact_no = models.CharField(max_length=15, blank=True, null=True,
                                            verbose_name=_("Alternate Contact Number"),
                                            help_text=_("Alternate Contact Number"))
    alternate_email = models.EmailField(blank=True, null=True,
                                        verbose_name=_("Alternate Email"),
                                        help_text=_("Alternate Email Address"))
    country = models.CharField(max_length=50, blank=True, null=True,
                               verbose_name=_("Country"),
                               help_text=_("Country"))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    subscription_expired = models.BooleanField(default=False,
                                               verbose_name=_("Subscription Expiry Date"),
                                               help_text=_("Expiry Date of current Subscription"))
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
"""
@receiver(post_save, sender=UserModel, dispatch_uid="create_firebase_account")
def create_firebase_account(sender, instance, created, *args, **kwargs):
    import firebase_admin
    from firebase_admin import auth, credentials
    from employee_management.settings import FIREBASE_CREDENTIAL_JSON
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
    data['password'] = "{}".format(instance.password)
    data['phone_number'] = "{}{}".format(country_code, instance.contact_number)
    print("post_save : signal", sender, instance, created, kwargs, args)
    try:
        DEFAULT_APP = firebase_admin.initialize_app(credentials.Certificate(FIREBASE_CREDENTIAL_JSON))
    except ValueError:
        print("app already exist....")
        pass
    if created:
        pass
        # user_create_response = auth.create_user(**data)
        # print(user_create_response)
"""
