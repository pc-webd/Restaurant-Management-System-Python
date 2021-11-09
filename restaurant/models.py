
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from .manager import UserManager
from django.conf import settings
from geopy.geocoders import Nominatim

#Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=30)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(default=False)
    is_subadmin=models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_by=models.CharField(max_length=100,null=True,blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.full_name

class UserAddresses(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='address')
    address=models.TextField(max_length=1000)
    pincode=models.CharField(max_length=30,null=True)
    lat=models.CharField(max_length=50,null=True,blank=True)
    lng=models.CharField(max_length=50,null=True,blank=True)

    def save(self, *args, **kwargs):
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(int(self.pincode))
        self.lat = location.latitude
        self.lng = location.longitude
        super(UserAddresses, self).save(*args, **kwargs)

    def __str__(self):  
        return self.address[0:30]

class Restaurant(models.Model):

    created_by=models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name=models.CharField(max_length=300)
    address=models.TextField(max_length=500)
    pincode=models.CharField(max_length=30,null=True)
    lat=models.CharField(max_length=50,null=True,blank=True)
    lng=models.CharField(max_length=50,null=True,blank=True)
    image=models.ImageField(upload_to='restaurant/')
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)

    def save(self, *args, **kwargs):
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(int(self.pincode))
        self.lat = location.latitude
        self.lng = location.longitude
        super(Restaurant, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
        
class Food(models.Model):
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE,null=True,related_name='food')
    name=models.CharField(max_length=300,null=True)
    price=models.FloatField(null=True)
    description=models.TextField(max_length=500,null=True)
    image=models.ImageField(upload_to='food/',null=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)
    updated_at=models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name