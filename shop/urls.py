from django.urls import path
from shop import views
from django.contrib.auth import views as auth_views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.home, name='category_filter'),
    path('product-category/<slug:slug>/', views.products, name='products'),
  
    path('add_to_cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:id>', views.update_cart, name='update_cart'),
    path('del_cart/<int:id>', views.remove_from_cart, name='del_cart'),
    path('cart-list', views.cart_list, name='cart-list'),
    path('buy_now', views.buy_now, name='buy_now'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('view_order/<int:id>', views.view_order, name='view_order'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('details/<int:id>/',views.detail,name="detail"),
    path('addreview/<int:id>/',views.add_review,name="add_review"),
    path('editreview/<int:product_id>/<int:review_id>',views.edit_review,name="edit_review"),
    path('deletereview/<int:product_id>/<int:review_id>',views.delete_review,name="delete_review"),
]
