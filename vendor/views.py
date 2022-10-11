from itertools import product
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from vendor.forms import ProductForm
from account.models import *
from account.forms import EditUserForm

# Create your views here.
def delete_product(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    messages.info(request,'Product Deleted Successfully')
    return redirect('vendor:products-list')



def add_product(request):
    vendors = User.objects.filter(is_vendor=True)
    categories = Category.objects.all()
    product_form = ProductForm()
    if request.method == 'POST':
        product_form = ProductForm(request.POST,request.FILES)
        if product_form.is_valid():
            product = Product()
            product.vendor_id = request.user.id
            product.name = request.POST['name']
            product.description = request.POST['description']
            product.price = request.POST['price']
            product.category_id = request.POST['category']
            product.image = request.FILES['image']
            product.save()
            messages.info(request,'Product Added successfully')
            return redirect('vendor:products-list')
        else:
            return render(request,'vendor/product-create.html',{'product_form':product_form})
    else:
        return render(request,'vendor/product-create.html',{'product_form':product_form,'categories':categories})


def edit_product(request,id):
    product = Product.objects.get(id=id)
    product_form = ProductForm(instance=product)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES,instance=product)
        if product_form.is_valid():
            product_form.save()
            messages.info(request,'Product Update successfully')
            return redirect('vendor:products-list')
        else:
            return render(request,'vendor/product-edit.html',{'product_form':product_form})
    else:
        return render(request,'vendor/product-edit.html',{'product_form':product_form})

def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'vendor/categories-list.html', {'categories': categories})


def products_list(request):
    products = Product.objects.filter(vendor=request.user)
    return render(request, 'vendor/products-list.html', {'products': products})



def edit_vendor(request,id):
    vendor = User.objects.get(id=id)
    vendor_form = EditUserForm(instance=vendor)
    if request.method == 'POST':
        vendor_form = EditUserForm(request.POST, instance=vendor)
        if vendor_form.is_valid():
            vendor_form.save()
            messages.info(request,'vendor Update successfully')
            return redirect('vendor:our-profile')
        else:
            return render(request,'vendor/vendor-edit.html',{'vendor_form':vendor_form})
    else:
        return render(request,'vendor/vendor-edit.html',{'vendor_form':vendor_form})

def vendor_list(request):
    vendor = User.objects.get(id=request.user.id)
    return render(request, 'vendor/vendor-list.html', {'vendor': vendor})


def update_order(request,id,status):
    product_order = ProductOrder.objects.get(id=id)
    product_order.order_status = status
    product_order.save()
    messages.info(request,'Order Details Updated Successfully')
    if status == 'Canceled':
        return redirect('vendor:canceled_orders')
    else:
        return redirect('vendor:delivered_orders')

def view_order(request,id):
    product_order = ProductOrder.objects.get(id=id)
    order_items = OrderDetails.objects.filter(product_order=product_order)
    return render(request,'vendor/view_order.html',{'product_order':product_order,'order_items':order_items})

def pending_orders(request):
    order_ids = OrderDetails.objects.filter(product__vendor=request.user).values_list('product_order_id',flat=True)
    product_orders = ProductOrder.objects.filter(id__in=order_ids,order_status='Pending')
    return render(request,'vendor/pending_orders.html',{'product_orders':product_orders})

def canceled_orders(request):
    order_ids = OrderDetails.objects.filter(product__vendor=request.user).values_list('product_order_id',flat=True)
    product_orders = ProductOrder.objects.filter(id__in=order_ids,order_status='Canceled')
    return render(request,'vendor/canceled_orders.html',{'product_orders':product_orders})

def delivered_orders(request):
    order_ids = OrderDetails.objects.filter(product__vendor=request.user).values_list('product_order_id',flat=True)
    product_orders = ProductOrder.objects.filter(id__in=order_ids,order_status='Delivered')
    return render(request,'vendor/delivered_orders.html',{'product_orders':product_orders})

