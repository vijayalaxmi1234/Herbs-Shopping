from itertools import product
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from account.forms import EditUserForm, UserLoginForm, UserRegistrationForm, CategoryForm, ProductForm
from account.models import *


def add_category(request):
    category_form = CategoryForm()
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.info(request,'Category Added successfully')
            return redirect('account:categories-list')
        else:
            return render(request,'administrator/category-create.html',{'category_form':category_form})
    else:
        return render(request,'administrator/category-create.html',{'category_form':category_form})


def delete_category(request,id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.info(request,'Category Deleted Successfully')
    return redirect('account:categories-list')
 
def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.info(request,'Product Deleted Successfully')
    return redirect('account:products-list')

def delete_vendor(request,id):
    vendor = User.objects.get(id=id)
    vendor.delete()
    messages.info(request,'vendor Deleted Successfully')
    return redirect('account:vendor-list')

def edit_category(request,id):
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.save()
        messages.info(request,'Category Updated Successfully')
        return redirect('account:categories-list')
    else:
        return render(request,'administrator/category-edit.html',{'category':category})


def add_product(request):
    vendors = User.objects.filter(is_vendor=True)
    categories = Category.objects.all()
    product_form = ProductForm()
    product_form.fields['vendor'].queryset = vendors
    if request.method == 'POST':
        product_form = ProductForm(request.POST,request.FILES)
        if product_form.is_valid():
            product_form.save()
            messages.info(request,'Product Added successfully')
            return redirect('account:products-list')
        else:
            return render(request,'administrator/product-create.html',{'product_form':product_form})
    else:
        return render(request,'administrator/product-create.html',{'product_form':product_form,'categories':categories})


def edit_product(request,id):
    product = Product.objects.get(id=id)
    product_form = ProductForm(instance=product)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES,instance=product)
        if product_form.is_valid():
            product_form.save()
            messages.info(request,'Product Update successfully')
            return redirect('account:products-list')
        else:
            return render(request,'administrator/product-edit.html',{'product_form':product_form})
    else:
        return render(request,'administrator/product-edit.html',{'product_form':product_form})

def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'administrator/categories-list.html', {'categories': categories})


def products_list(request):
    products = Product.objects.all()
    return render(request, 'administrator/products-list.html', {'products': products})



def edit_vendor(request,id):
    vendor = User.objects.get(id=id)
    vendor_form = EditUserForm(instance=vendor)
    if request.method == 'POST':
        vendor_form = EditUserForm(request.POST, instance=vendor)
        if vendor_form.is_valid():
            vendor_form.save()
            messages.info(request,'vendor Update successfully')
            return redirect('account:vendor-list')
        else:
            return render(request,'administrator/vendor-edit.html',{'vendor_form':vendor_form})
    else:
        return render(request,'administrator/vendor-edit.html',{'vendor_form':vendor_form})

def vendor_list(request):
    vendors = User.objects.filter(is_vendor=True)
    return render(request, 'administrator/vendor-list.html', {'vendors': vendors})


def admin_dashboard(request):
    total_customers = User.objects.filter(is_vendor=False).count()
    total_vendors = User.objects.filter(is_vendor=True).count()
    total_products = Product.objects.all().count()
    total_orders = ProductOrder.objects.all().count()
    return render(request,'administrator/index.html',{'total_customers':total_customers,'total_orders':total_orders,'total_products':total_products,'total_vendors':total_vendors})

def vendor_dashboard(request):
    return render(request,'vendor/index.html')    


def about(request):
    return render(request,'shop/about.html')

def contact(request):
    return render(request,'shop/contact.html')


def admin_dashboard(request):
    return render(request,'administrator/index.html')

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, email=data['email'], password=data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'login successfully', 'success')
                if user.is_admin:
                    return redirect('account:admin_dashboard')
                elif user.is_vendor:
                    return redirect('account:vendor_dashboard')    
                return redirect('shop:home')
            else:
                messages.error(request, 'username or password is wrong', 'danger')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})



def user_logout(request):
    logout(request)
    messages.success(request, 'logout successfully', 'success')
    return redirect('shop:home')






def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(data['email'], data['full_name'], data['phone_number'], data['password'])
            messages.success(request, 'you registered successfully', 'success')
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def vendor_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_vendor(data['email'], data['full_name'], data['phone_number'], data['password'])
            messages.success(request, 'You registered successfully', 'success')
            return redirect('/')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/vendor_register.html', {'form': form})

def update_order(request,id,status):
    product_order = ProductOrder.objects.get(id=id)
    product_order.order_status = status
    product_order.save()
    messages.info(request,'Order Details Updated Successfully')
    if status == 'Canceled':
        return redirect('account:canceled_orders')
    else:
        return redirect('account:delivered_orders')

def view_order(request,id):
    product_order = ProductOrder.objects.get(id=id)
    order_items = OrderDetails.objects.filter(product_order=product_order)
    return render(request,'administrator/view_order.html',{'product_order':product_order,'order_items':order_items})

def pending_orders(request):
    product_orders = ProductOrder.objects.filter(order_status='Pending')
    return render(request,'administrator/pending_orders.html',{'product_orders':product_orders})

def canceled_orders(request):
    product_orders = ProductOrder.objects.filter(order_status='Canceled')
    return render(request,'administrator/canceled_orders.html',{'product_orders':product_orders})

def delivered_orders(request):
    product_orders = ProductOrder.objects.filter(order_status='Delivered')
    return render(request,'administrator/delivered_orders.html',{'product_orders':product_orders})

def pending_bookings(request):
    bookings = ServiceBooking.objects.filter(booking_status='Pending')
    return render(request,'administrator/pending_bookings.html',{'bookings':bookings})

def assign_vendor(request,id):
    vendors = Vendor.objects.all()
    booking = ServiceBooking.objects.get(id=id)
    if request.method == 'POST':
        booking.vendor_id = request.POST['vendor_id']
        booking.booking_status = 'Assigned'
        booking.save()
        messages.info(request,'vendor Assigned Successfully')
        return redirect('account:assigned_bookings')
    else:
        return render(request,'administrator/assign_vendor.html',{'booking':booking,'vendors':vendors})

def assigned_bookings(request):
    bookings = ServiceBooking.objects.filter(booking_status='Assigned')
    return render(request,'administrator/assigned_bookings.html',{'bookings':bookings})

def canceled_bookings(request):
    bookings = ServiceBooking.objects.filter(booking_status='Canceled')
    return render(request,'administrator/canceled_bookings.html',{'bookings':bookings})

def completed_bookings(request):
    bookings = ServiceBooking.objects.filter(booking_status='Completed')
    return render(request,'administrator/completed_bookings.html',{'bookings':bookings})

def update_booking(request,id,status):
    booking = ServiceBooking.objects.get(id=id)
    booking.booking_status = status
    booking.save()
    messages.info(request,'Booking Details Updated Successfully')
    if status == 'Canceled':
        return redirect('account:canceled_bookings')
    else:
        return redirect('account:completed_bookings')

