from django.urls import path
from . import views

app_name = 'wadmin'

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    
    # Profile URLs
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Category URLs
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
    # Product URLs
    path('products/', views.manage_products, name='manage_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Product Image URLs
    path('product/image/delete/<int:image_id>/', views.delete_product_image, name='delete_product_image'),
    path('product/image/set-primary/<int:image_id>/', views.set_primary_image, name='set_primary_image'),
    path('product/images/reorder/<int:product_id>/', views.reorder_images, name='reorder_images'),
]