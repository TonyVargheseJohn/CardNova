from django.urls import path
from . import views

app_name = 'guest'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('login/', views.login, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout, name='logout'),
]