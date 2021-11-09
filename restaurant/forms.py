from django import forms
from django.db import models
from django.db.models import fields
from django.forms import widgets
from django.forms.widgets import PasswordInput, Textarea
from .models import Food, Restaurant, User,UserAddresses

class UserForm(forms.ModelForm):
    password=forms.CharField(widget=PasswordInput,min_length=8,required=True)
    class Meta:
        model=User
        fields=['email','full_name','password']

    def clean_password(self):
        password=self.cleaned_data['password']
        if len(password)<8:
            raise forms.ValidationError("Your password should be at least 8 Characters ")
      
        return password

class UserAddresseForm(forms.ModelForm):
    address=forms.CharField(widget=Textarea(attrs={'cols':40,'rows':4}))
    class Meta:
        model=UserAddresses
        fields=['address','pincode']
    
class RestaurantForm(forms.ModelForm):
    address=forms.CharField(widget=Textarea(attrs={'cols':40,'rows':3}))
    class Meta:
        model=Restaurant
        fields=['name','address','pincode','image']

class FoodForm(forms.ModelForm):
    description=forms.CharField(widget=Textarea(attrs={'cols':40,'rows':2}))
    class Meta:
        model=Food
        fields=['name','price','description','image']
