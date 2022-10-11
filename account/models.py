from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.urls import reverse
from account.managers import MyUserManager
from django.utils.timezone import now
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from account.constants import PaymentStatus

class User(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def get_absolut_url(self):
        return reverse('shop:category_filter', args={self.slug})

class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%b/%d/')
    description = models.TextField()
    price = models.IntegerField()
    current_stock = models.IntegerField(default=10)
    averagerating=models.FloatField(default=0)
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def get_absolut_url(self):
        return reverse('shop:product_detail', args={self.slug, })

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)
    rating = models.FloatField(default=0)

class ProductOrder(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    order_date = models.DateTimeField(default=now)
    order_status = models.CharField(max_length=12,default='Pending')
    shipping_address = models.CharField(max_length=200,blank=True)
    total_order_amount = models.IntegerField(default=10)
    status = models.CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(
        _("Order ID"), max_length=40, null=False, blank=False
    )
    payment_id = models.CharField(
        _("Payment ID"), max_length=36, null=False, blank=False
    )
    signature_id = models.CharField(
        _("Signature ID"), max_length=128, null=False, blank=False
    )

class OrderDetails(models.Model):
	product_order = models.ForeignKey(ProductOrder, null=True, on_delete=models.SET_NULL)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	price = models.IntegerField(default=10)
	amount = models.IntegerField(default=10)

class CartItem(models.Model):
	user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
	product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
	quantity = models.IntegerField(default=1)
	amount = models.IntegerField(default=1)

