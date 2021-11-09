from django.urls import path
from . import views

app_name='restaurant'

urlpatterns=[
    path('',views.index,name='home'),
    path('register/',views.registerUser,name='register'),
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('delete-address/<int:id>',views.deleteAddress,name='delete-address'),
    path('admin-dashboard/',views.adminDashboard,name='admin-dashboard'),
    path('subadmin-dashboard/',views.subadminDashboard,name='subadmin-dashboard'),
    path('add-to-subadmin/<int:id>',views.addToSubadmin,name='add-to-subadmin'),
    path('user/<int:id>',views.userDetail,name='view-user'),
    path('delete-user/<int:id>',views.userDelete,name='delete-user'),
    path('add-restaurant',views.addRestaurant,name='add-restaurant'),
    path('restaurant/<int:resID>/menu/',views.restaurantMenu,name='menu'),
    path('delete-food/<int:id>',views.deleteFood,name='delete-food'),
    path('update-food/<int:id>',views.updateFood,name='update-food'),
    path('delete-restaurant/<int:id>',views.deleteRestaurant,name='delete-res'),
    path('change_password/',views.changePassword,name='change_password'),
    path('add-address/',views.addAddress,name='add-address'),
    path('search/restaurant/',views.searchRestaurant,name='search'),
]