from django.urls import path

from .views import *
from django.contrib.auth import views as auth_views

app_name = "vendor"

urlpatterns = [
    path('products-list/', products_list, name='products-list'),
    path('product-create/', add_product, name='product-create'),
    path('product-edit/<int:id>', edit_product, name='product_edit'),
    path('product-delete/<int:id>', delete_product, name='product_delete'),
    path('categories-list/', categories_list, name='categories-list'),
    path('our-profile', vendor_list, name='our-profile'),
    path('edit-profile/<int:id>', edit_vendor, name='vendor_edit'),
    path('update_order/<int:id>/<str:status>', update_order, name='update_order'),
    path('view_order/<int:id>', view_order, name='view_order'),
    path('pending_orders/', pending_orders, name='pending_orders'),
    path('canceled_orders/', canceled_orders, name='canceled_orders'),
    path('delivered_orders/', delivered_orders, name='delivered_orders'),
]
