from django.contrib import admin
from .models import Food, User,UserAddresses,Restaurant

# Register your models here.
admin.site.register(User)
admin.site.register(UserAddresses)
admin.site.register(Restaurant)
admin.site.register(Food)