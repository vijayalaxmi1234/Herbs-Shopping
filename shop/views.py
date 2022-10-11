import json
import re
from unicodedata import category
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from account.models import CartItem, OrderDetails, Product,User, Category, ProductOrder, Review
from django.db.models import Sum
from django.db.models import Avg
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from account.constants import PaymentStatus
from account.forms import EditUserForm, ReviewForm
 
# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def home(request, slug=None):
    products = Product.objects.filter(status=True)
    categories = Category.objects.all()
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)
    return render(request, 'shop/home.html', {'products': products, 'categories': categories})

def detail(request,id):
    product=Product.objects.get(id=id)
    reviews = Review.objects.filter(product=id).order_by("-comment")

    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average == None:
        average=0
    else:
        average = round(average,2)
    context={
        "product":product,
        "reviews":reviews,
        "average":average,
    }
    return render(request,'shop/details.html',context)

def products(request, slug=None):
    products = Product.objects.filter(status=True)
    categories = Category.objects.all()
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)
    return render(request, 'shop/products.html', {'products': products,"cat":category, 'categories': categories})


def product_detail(request, slug):
    categories = Category.objects.all()
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product, 'categories': categories})

def remove_from_cart(request,id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.delete()
    messages.info(request,'Cart Item removed Successfully')
    return redirect('shop:cart-list')

def buy_now(request):
    cart_items = CartItem.objects.filter(user=request.user)
    tot_amount = 0
    asum = CartItem.objects.filter(user=request.user).aggregate(Sum('amount'))
    if asum is None:
        tot_amount = 0
    else:
        tot_amount = asum['amount__sum']
    razorpay_order = razorpay_client.order.create(
        {"amount": int(tot_amount) * 100, "currency": "INR", "payment_capture": "1"}
    )
    product_order = ProductOrder()
    product_order.user = request.user
    product_order.provider_order_id=razorpay_order["id"]
    product_order.shipping_address = request.POST['shipping_address']
    product_order.total_order_amount = tot_amount
    product_order.save()

    for cart_item in cart_items:
        order_detail = OrderDetails()
        order_detail.product_order = product_order
        order_detail.amount = cart_item.amount
        order_detail.quantity = cart_item.quantity
        order_detail.product = cart_item.product
        order_detail.save()
        cart_item.delete()
    return render(
        request,
        "shop/payment.html",
        {
            "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
            "razorpay_key": settings.RAZOR_KEY_ID,
            "order": product_order,
        },
    )


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
 
    def verify_signature(response_data):
        return razorpay_client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = ProductOrder.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            order_items = OrderDetails.objects.filter(product_order=order)
            for order_item in order_items:
                product = order_item.product
                qty = order_item.quantity
                product.current_stock = product.current_stock - qty
                product.save()
            messages.info(request,'Your Payment for the order is successfull')
            return redirect('shop:my_orders')
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            messages.info(request,'Your Payment for the order is not successfull')
            return redirect('shop:my_orders')
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        provider_order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = ProductOrder.objects.get(provider_order_id=provider_order_id)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        messages.info(request,'Your Payment for the order is not successfull')
        return redirect('shop:my_orders')


def update_cart(request,id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.quantity = request.POST['quantity']
    cart_item.amount = cart_item.product.price * int(request.POST['quantity'])
    cart_item.save()
    messages.info(request,'Cart Updated Successfully')
    return redirect('shop:cart-list')

def cart_list(request):
    categories = Category.objects.all()
    cart_items = CartItem.objects.filter(user=request.user)
    tot_amount = 0
    asum = CartItem.objects.filter(user=request.user).aggregate(Sum('amount'))
    if asum is None:
        tot_amount = 0
    else:
        tot_amount = asum['amount__sum']
    return render(request, 'shop/cart-list.html', {'cart_items': cart_items, 'categories': categories,'tot_amount':tot_amount})


def add_to_cart(request,id):
    product = Product.objects.get(id=id)
    try:
        cart_item = CartItem.objects.get(product=product,user=request.user)
        cart_item.quantity = cart_item.quantity + 1
        cart_item.amount = cart_item.amount + product.price
    except CartItem.DoesNotExist:
        cart_item = CartItem()
        cart_item.product = product
        cart_item.user = request.user
        cart_item.quantity = 1
        cart_item.amount = product.price
    cart_item.save()
    messages.info(request,'Product Added to Cart Successfully')
    return redirect('shop:cart-list')



def my_orders(request):
    categories = Category.objects.all()
    product_orders = ProductOrder.objects.filter(user=request.user)
    return render(request,'shop/my_orders.html',{'product_orders':product_orders, 'categories': categories})

def view_order(request,id):
    categories = Category.objects.all()
    product_order = ProductOrder.objects.get(id=id)
    order_items = OrderDetails.objects.filter(product_order=product_order)
    return render(request,'shop/view_order.html',{'product_order':product_order,'order_items':order_items,'categories': categories})

def invoice(request,id):
    categories = Category.objects.all()
    product_order = ProductOrder.objects.get(id=id)
    order_items = OrderDetails.objects.filter(product_order=product_order)
    return render(request,'shop/invoice.html',{'product_order':product_order,'order_items':order_items,'categories': categories})


def my_profile(request):
    return render(request,'shop/my_profile.html')

def edit_profile(request):
    user_form = EditUserForm(data={'full_name':request.user.full_name,'email':request.user.email,'phone_number':request.user.phone_number})
    if request.method == 'POST':
        user_form = EditUserForm(request.POST)
        if user_form.is_valid():
           data = user_form.cleaned_data
           user = User.objects.get(id=request.user.id)
           user.full_name = data['full_name']
           user.phone_number = data['phone_number']
           user.email = data['email']
           user.save()
           messages.info(request,'Profile Updated Successfully')
           return redirect('shop:my_profile')
        else:
            return render(request,'shop/edit_profile.html',{'user_form':user_form})
    else:
        return render(request,'shop/edit_profile.html',{'user_form':user_form})


def add_review(request,id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        if request.method == "POST":
            form = ReviewForm(request.POST or None)
            if form.is_valid():
                data = form.save(commit=False)
                data.comment = request.POST["comment"]
                data.rating = request.POST["rating"]
                data.user = request.user
                data.product = product
                data.save()
                return redirect("shop:detail",id)
        else:
            form = ReviewForm()
        return render(request,'shop/details.html',{'form':form})
    else:
        return redirect("accounts:login")

def edit_review(request,product_id,review_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        review = Review.objects.get(product=product, id=review_id)
        if request.user == review.user:
            if request.method == "POST":
                form = ReviewForm(request.POST,instance=review)
                if form.is_valid():
                    data = form.save(commit=False)
                    if (data.rating>10) or (data.rating<0):
                        error="Out of range. Please select rating from 0 to 10."
                        return render(request,'shop/editreview.html',{'error':error, "form":form})
                    else:
                        data.save()
                        return redirect("shop:detail",product_id)
            else:
                form = ReviewForm(instance=review)
            return render(request,'shop/editreview.html',{"form":form})
        else:
            return redirect("shop:detail",product_id)
    else:
        return redirect("accounts:login")

def delete_review(request,product_id,review_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        review = Review.objects.get(product=product, id=review_id)
        if request.user == review.user:
            review.delete()
        return redirect("shop:detail",product_id)
    else:
        return redirect("accounts:login")