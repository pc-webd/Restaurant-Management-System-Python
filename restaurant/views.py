
from django import forms
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from restaurant.forms import FoodForm, UserForm,UserAddresseForm,RestaurantForm
from .models import *
from django.core.mail import send_mail  
from geopy.distance import  great_circle
# Create your views here.

def index(request):
    return render(request,'restaurant/index.html')

def registerUser(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method=='GET':
        form=UserForm(None)
        return render(request,'restaurant/register.html',{'form':form})
    elif request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()
            send_mail_after_registration(email)
            user=authenticate(email=email,password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    messages.success(request,'Your account has been successfully created.')
                    return redirect('/dashboard/')
                else:
                    return HttpResponse("Oops! Something went wrong, your Account has been deleted/deactivate")
        else:
            return render(request,'restaurant/register.html',{'form':form})
    
def send_mail_after_registration(email):
    subject="Your Account has been created successfully"
    message=f'Thank you for sign up.'
    email_from=settings.EMAIL_HOST_USER
    receipent_list=[email]
    send_mail(subject,message,email_from,receipent_list)

def loginUser(request):
    if request.method=='GET':
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/admin-dashboard/')
            elif request.user.is_subadmin:
                return redirect('/subadmin-dashboard/')
            else:
                return redirect('/dashboard/')
        return render(request,'restaurant/login.html')
    elif request.method== 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        if email == '' or password =='':
            return render(request,'restaurant/login.html',{'error_msg':'both are required fields'})
        user=authenticate(email=email,password=password)
        if user is not None:
            if user.is_active:
                if user.is_staff:
                    login(request,user)
                    messages.success(request,'You are successfully logged in.')
                    return redirect('/admin-dashboard/')
                elif user.is_subadmin:
                    login(request,user)
                    messages.success(request,'You are successfully logged in.')
                    return redirect('/subadmin-dashboard/')
                else:
                    login(request,user)
                    messages.success(request,'You are successfully logged in.')
                    return redirect('/dashboard/')
            else:
                return HttpResponse('Your Account has been disabled')
        else:
            return render(request,'restaurant/login.html',{'error_msg':'your username or password is incorrect'})

def logoutUser(request):
    logout(request)
    messages.success(request,'Your are successfully logged out.')
    return redirect('/login/')

@login_required
def dashboard(request):
    if request.method=='GET':
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('/admin-dashboard/')
            elif request.user.is_subadmin:
                return redirect('/subadmin-dashboard/')
        try:
            address_obj=UserAddresses.objects.filter(user=request.user)
            restaurant_list=Restaurant.objects.select_related('created_by').all().order_by('-created_at')
            print(restaurant_list)
        except Exception as e:
            return HttpResponse(e)
        form=UserAddresseForm(None)
        context={
            'form':form,
            'addresses':address_obj,
            'restaurant':restaurant_list
        }
        return render(request,'restaurant/welcome.html',context)
    elif request.method=='POST':
        form=UserAddresseForm(request.POST)
        if form.is_valid():
            address=form.cleaned_data['address']
            pincode=form.cleaned_data['pincode']
            if pincode:
                geolocator = Nominatim(user_agent="geoapiExercises")
                location = geolocator.geocode(int(pincode))
                lat = location.latitude
                lng = location.longitude 

                address_obj=UserAddresses(user=request.user,address=address,pincode=pincode,lat=lat,lng=lng)
                address_obj.save()
                messages.success(request,'adddress has been added')
                return redirect('/dashboard/')
        return render(request,'restaurant/welcome.html',{'form':form})

@login_required
def deleteAddress(request,id):
    delete_obj=UserAddresses.objects.get(user=request.user,id=id)
    delete_obj.delete()
    messages.info(request,'Address has been deleted.')
    if request.user.is_subadmin:
        return redirect('/subadmin-dashboard/')
    else:
        return redirect('/dashboard/')

@login_required
def adminDashboard(request):
    if request.method=='GET':
        if request.user.is_authenticated:
            if not request.user.is_staff:
                if request.user.is_subadmin:
                    return redirect('/subadmin-dashboard/')
                else:
                    return redirect('/dashboard/')
        try:
            user_list=User.objects.all().exclude(email=request.user).order_by('-date_joined')
            restaurant_list=Restaurant.objects.select_related('created_by').all().exclude(created_by=request.user).order_by('-created_at')
            loginUser_restaurant_list=Restaurant.objects.select_related('created_by').filter(created_by=request.user).order_by('-created_at')
            form=UserForm(request.POST or None)
        except Exception as e:
            return HttpResponse(e)
        context={
            'users':user_list,
            'form':form,
            'restaurant':restaurant_list,
            'user_restaurant_list':loginUser_restaurant_list,
        }
        return render(request,'restaurant/admin_dashboard.html',context)

    elif request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()
            a=user
            a.created_by=request.user.email
            a.save()
            messages.success(request,"User has been succesfully created")
            return redirect('/admin-dashboard/')
        else:
            messages.warning(request,form.errors)
            return redirect('/admin-dashboard/')

@login_required
def subadminDashboard(request):
    if request.method=='GET':
        if request.user.is_authenticated:
            if not request.user.is_subadmin:
                if request.user.is_staff:
                    return redirect('/admin-dashboard/')
                else:
                    return redirect('/dashboard/')
        try:
            user_list=User.objects.filter(created_by=request.user.email).order_by('-date_joined')
            restaurant_list=Restaurant.objects.select_related('created_by').all().exclude(created_by=request.user).order_by('-created_at')
            loginUser_restaurant_list=Restaurant.objects.select_related('created_by').filter(created_by=request.user).order_by('-created_at')
            form=UserForm(request.POST or None)
        except Exception as e:
            return HttpResponse(e)
        context={
            'users':user_list,
            'form':form,
            'restaurant':restaurant_list,
            'user_restaurant_list':loginUser_restaurant_list
        }
        return render(request,'restaurant/admin_dashboard.html',context)

    elif request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()
            a=user
            a.created_by=request.user.email
            a.save()
            messages.success(request,"User has been succesfully created")
            return redirect('/admin-dashboard/')
        else:
            messages.warning(request,form.errors)
            return redirect('/admin-dashboard/')

# create subadmin
@login_required
def addToSubadmin(request,id):
    try:
        user=User.objects.get(pk=id)
        if user is not None:
            user.is_subadmin='True'
            user.save()
            messages.success(request,"User has been succesfully added to subadmin")
            return redirect('/admin-dashboard/') 
        else:
            messages.warning(request,'User not found')
            return redirect('/admin-dashboard/') 
    except Exception as e:
        return HttpResponse(e)
    
@login_required
def userDetail(request,id):
    if request.user.is_staff:
        users=get_object_or_404(User,pk=id)
        return render(request,'restaurant/userdetail.html',{'user':users})
    elif request.user.is_subadmin:
        users=get_object_or_404(User,pk=id,created_by=request.user.email)
        return render(request,'restaurant/userdetail.html',{'user':users})
    else:
        return HttpResponse('Sorry, you are not admin.please <a href="/dashboard/">go back to home page</a>')

    
@login_required
def userDelete(request,id):
    if request.user.is_staff:
        users=get_object_or_404(User,pk=id)
        users.delete()
        messages.success(request,'user has been deleted.')
        return redirect('/admin-dashboard/')
    elif request.user.is_subadmin:
        users=get_object_or_404(User,pk=id,created_by=request.user.email)
        users.delete()
        messages.success(request,'user has been deleted.')
        return redirect('/subadmin-dashboard/')
    else:
        return HttpResponse('Sorry, you are not admin.please <a href="/dashboard/">go back to home page</a>')


@login_required
def addRestaurant(request):
    if request.method=='GET':
        if request.user.is_authenticated:
            if not request.user.is_staff | request.user.is_subadmin:
                return redirect('/dashboard/')
        form=RestaurantForm(None)
        return render(request,'restaurant/add_restaurant.html',{'form':form})
        
    elif request.method=='POST':
        form=RestaurantForm(request.POST,request.FILES)
        if form.is_valid():
            name=form.cleaned_data['name']
            address=form.cleaned_data['address']
            pincode=form.cleaned_data['pincode']
            image=form.cleaned_data['image']
            if pincode:
                geolocator = Nominatim(user_agent="geoapiExercises")
                location = geolocator.geocode(int(pincode))
                lat = location.latitude
                lng = location.longitude 
                res_obj=Restaurant(created_by=request.user,name=name,address=address,pincode=pincode,lat=lat,lng=lng,image=image)
                res_obj.save()
                get_current_res=res_obj.id
                messages.info(request,'Restaurant has been added')
                return redirect('restaurant:menu',resID=get_current_res)
        return render(request,'restaurant/add_restaurant.html',{'form':form})

@login_required
def restaurantMenu(request,resID):
    if request.method=='GET':
        restaurant=get_object_or_404(Restaurant,id=resID)
        menu=restaurant.food.select_related('restaurant').all()
        context={
            'restaurant':restaurant,
            'menu':menu
        }
        return render(request,'restaurant/food.html',context)
    if request.method=='POST':
        resID=request.POST.get('id')
        restaurant_obj=Restaurant.objects.get(id=resID)
        name= request.POST.getlist('foodName')
        price= request.POST.getlist('price')
        image= request.FILES.getlist('image')
        desc= request.POST.getlist('desc')

        for i in range(len(name)):
            food_obj=Food.objects.create(restaurant=restaurant_obj,name=name[i],price=price[i],image=image[i],description=desc[i])
            food_obj.save()
            
        messages.success(request,'Menu has been Updated.')
        return redirect('restaurant:menu',resID=resID)

@login_required
def deleteFood(request,id):
    if request.user.is_authenticated:
        res_obj=get_object_or_404(Restaurant,food__id=id)
        if not request.user==res_obj.created_by:
            return HttpResponse('Sorry, this request is not possible')
        get_food=get_object_or_404(Food,id=id)
        get_food.delete()
        messages.success(request,'Food has been deleted.')
        return redirect('restaurant:menu',resID=res_obj.id)


@login_required
def updateFood(request,id):
    if request.user.is_authenticated:

        food_obj=get_object_or_404(Food,id=id,restaurant__created_by=request.user)
        get_restaurant=food_obj.restaurant
        menu=get_restaurant.food.select_related('restaurant').all()
        
        form = FoodForm(request.POST or request.FILES or None, instance = food_obj)

        # save the data from the form and
        # redirect to detail_view

        context={
            'current_food':food_obj,
            'restaurant':get_restaurant,
            'menu':menu,
            'form':form
        }
        if form.is_valid():
            form.save()
            messages.success(request,'Food has been updated.')
            return redirect('restaurant:menu',resID=get_restaurant.id)

        return render(request,'restaurant/food.html',context)   


@login_required
def deleteRestaurant(request,id):
    if request.user.is_authenticated:
        res_obj=get_object_or_404(Restaurant,id=id,created_by=request.user)
        res_obj.delete()
        messages.success(request,'Restaurant has been deleted.')
        if request.user.is_staff:
            return redirect('/admin-dashboard/')
        else:
            return redirect('/subadmin-dashboard/')


@login_required
def changePassword(request):
    if request.method=='GET':
        return render(request,'restaurant/change_password.html')
    if request.method=='POST':
        old_psw=request.POST.get('old_psw')
        new_psw=request.POST.get('new_psw')
        
        if old_psw =='' or new_psw=='':
            messages.success(request,'Fields are required.')
            return render(request,'restaurant/change_password.html')
        
        user= authenticate(email=request.user.email,password=old_psw)
        if user is not None:
            if user.is_active:
                user.set_password(new_psw)
                user.save()
                messages.success(request,'Password has been updated.')
                logout(request)
                return redirect('/login/')
        else:
            messages.warning(request,'Your password is incorrect')
            return render(request,'restaurant/change_password.html')

@login_required
def addAddress(request):
    if request.method=='POST':
        address=request.POST.get('address')
        pincode=request.POST.get('pincode')

        if address=='' or pincode=='':
            messages.warning(request,'Fields are required')
            return redirect('/subadmin-dashboard/')
        if pincode:
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode(int(pincode))
            lat = location.latitude
            lng = location.longitude 
            address_obj=UserAddresses(user=request.user,address=address,pincode=pincode,lat=lat,lng=lng)
            address_obj.save()

            messages.success(request,'Address has been added')
            return redirect('/subadmin-dashboard/')

@login_required
def searchRestaurant(request):
    query = request.GET.get("query")
    address_id=request.GET.get('address')
    if address_id:
        address_obj=get_object_or_404(UserAddresses,pk=address_id)
        lat = address_obj.lat
        lng=address_obj.lng

    if query:
        restaurant_objs = Restaurant.objects.select_related('created_by').filter(
            Q(name__icontains=query) | Q(address__icontains=query) |
            Q(pincode__icontains=query) | Q(food__name__icontains=query)).distinct()

        if address_id:
            payload=[]
            for restaurant_obj in restaurant_objs:
                result = {}
                result['id']=restaurant_obj.id
                result['name'] = restaurant_obj.name
                result['image'] = restaurant_obj.image
                result['address']= restaurant_obj.address
                result['pincode'] = restaurant_obj.pincode
                first = (float(lat) , float(lng))
                second = (float(restaurant_obj.lat) , float(restaurant_obj.lng))
                result['distance'] = int( great_circle(first , second).miles)
                payload.append(result)
            print(payload)
            return render(request, 'restaurant/search_restaurant.html', {'query':query,'restaurant':payload})
        return render(request, 'restaurant/search_restaurant.html', {'query':query,'restaurant':restaurant_objs})

