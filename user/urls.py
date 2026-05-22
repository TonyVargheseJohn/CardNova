from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Cart - Use the correct function names from views.py
    path('cart/', views.cart_view, name='cart_view'),  # Changed from 'cart' to 'cart_view'
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Logout
    path('logout/', views.logout, name='logout'),
]