from django.urls import path

from account import views
from django.contrib.auth import views as auth_views

app_name = "account"

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('products-list/', views.products_list, name='products-list'),
    path('product-create/', views.add_product, name='product-create'),
    path('product-edit/<int:id>', views.edit_product, name='product_edit'),
    path('product-delete/<int:id>', views.delete_product, name='product_delete'),
    path('categories-list/', views.categories_list, name='categories-list'),
    path('category-create/', views.add_category, name='category-create'),
    path('category-edit/<int:id>', views.edit_category, name='category_edit'),
    path('category-delete/<int:id>', views.delete_category, name='category_delete'),
    path('vendor-list/', views.vendor_list, name='vendor-list'),
    path('vendor-edit/<int:id>', views.edit_vendor, name='vendor_edit'),
    path('vendor-delete/<int:id>', views.delete_vendor, name='vendor_delete'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('vendor_register/', views.vendor_register, name='vendor_register'),
    path('update_order/<int:id>/<str:status>', views.update_order, name='update_order'),
    path('view_order/<int:id>', views.view_order, name='view_order'),
    path('pending_orders/', views.pending_orders, name='pending_orders'),
    path('canceled_orders/', views.canceled_orders, name='canceled_orders'),
    path('delivered_orders/', views.delivered_orders, name='delivered_orders'),
    
    path('update_booking/<int:id>/<str:status>', views.update_booking, name='update_booking'),
    path('assign_vendor/<int:id>', views.assign_vendor, name='assign_vendor'),
    # Change Password
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='administrator/change_password.html',
            success_url = '/accounts/logout/'
        ),
        name='change_password'
    ),
     path(
        'vendor-change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='vendor/change_password.html',
            success_url = '/accounts/logout/'
        ),
        name='vendor_change_password'
    ),
    path(
        'customer-change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='shop/change_password.html',
            success_url = '/accounts/logout/'
        ),
        name='customer_change_password'
    ),
]
