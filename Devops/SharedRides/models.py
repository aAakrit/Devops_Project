from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,  PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
import datetime


request_choices = (('P', 'Pending'), ('A', 'Accepted'), ('D', 'Declined'))

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        
        return self.create_user(email, password, **extra_fields)



class ContactNumberValidator(RegexValidator):
    regex = r'^\+?1?\d{9,15}$'
    message = _(
        'Enter a valid phone number. It may start with + and contain up to 15 digits.'
    )
    flags = 0

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    ##Profile Detail Fields
    first_name = models.CharField(max_length=128,verbose_name="First Name", null=True)
    last_name = models.CharField(max_length=128,verbose_name="Last Name", null=True)
    contact_number = models.BigIntegerField(verbose_name="Contact Number", validators=[ContactNumberValidator], null=True)

    objects = CustomUserManager()


    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    @property
    def is_authenticated(self):
        return True

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_confirmed_trips(self):
        return Trip.objects.filter(user=self)

    def accept_request(self, req):
        if req.trip.user == self:
            req.accept()
            return True
        else:
            return False

    def decline_request(self, req):
        if req.trip.user == self:
            req.decline()
            return True
        else:
            return False

    def current_received_requests(self):
        return Request.objects.filter(trip__user=self, trip__time__gt=datetime.datetime.now(), status='P').order_by(
            'trip__time')

    def current_sent_requests(self):
        return Request.objects.filter(from_user=self, trip__time__gt=datetime.datetime.now()).order_by('trip__time')

    def previous_received_requests(self):
        return Request.objects.filter(trip__user=self, trip__time__lt=datetime.datetime.now(), status='P').order_by(
            '-trip__time')

    def previous_sent_requests(self):
        return Request.objects.filter(from_user=self, trip__time__lt=datetime.datetime.now()).order_by('-trip__time')


class Trip(models.Model):
    user = models.ForeignKey(CustomUser, null=False,default=None, blank=False, related_name='hosted_trips', on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    cluster = models.TextField(default='[]')
    travel_distance = models.FloatField(null=False, blank=False,default=0.0)
    start_place = models.TextField(verbose_name="Starting Place", null=False, blank=True)
    end_place = models.TextField(verbose_name="Ending Place", null=False, blank=True)
    participants = models.ManyToManyField(CustomUser, related_name='participant_trips', blank=True)

    def __unicode__(self):
        return self.start_place + " - " + self.end_place + " on " + str(self.time)


class Request(models.Model):
    from_user = models.ForeignKey(CustomUser, null=False,on_delete=models.CASCADE, blank=False)
    trip = models.ForeignKey(Trip, null=False,on_delete=models.CASCADE, blank=False)
    start_lat = models.FloatField(null=False, blank=False)
    start_lng = models.FloatField(null=False, blank=False)
    end_lat = models.FloatField(null=False, blank=False)
    end_lng = models.FloatField(null=False, blank=False)
    start_place = models.TextField(verbose_name="Pick-up Location", null=False, blank=True)
    end_place = models.TextField(verbose_name="Drop-off Location", null=False, blank=True)
    status = models.CharField(max_length=20, choices=request_choices)

    def __str__(self):
        return f"{self.from_user} to {self.trip.user} - {self.trip}"

    def accept(self):
        self.trip.participants.add(self.from_user)
        self.status = 'A'
        self.save()

    def decline(self):
        self.status = 'D'
        self.save()
