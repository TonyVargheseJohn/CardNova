from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.db.models import Q, Sum
from guest.models import User
from wadmin.models import Product, Category
from functools import wraps
from .models import Cart

# User Login Decorator
def user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('uid') or request.session.get('user_id')
        
        if not user_id:
            messages.error(request, 'Please login to continue.')
            return redirect('guest:login')
        
        try:
            request.current_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            request.session.flush()
            messages.error(request, 'User not found. Please login again.')
            return redirect('guest:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def _get_cart_query(request):
    """Returns Q filter for current user"""
    if request.session.get('uid') or request.session.get('user_id'):
        user_id = request.session.get('uid') or request.session.get('user_id')
        return Q(user_id=user_id)
    return Q(pk=None)  # Empty cart fallback

@user_required
def home(request):
    """User dashboard home page"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'user/home.html', {
        'current_user': request.current_user,
        'products': products,
        'categories': categories,
    })

@user_required
def profile(request):
    """View user profile"""
    return render(request, 'user/profile.html', {
        'current_user': request.current_user
    })

@user_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone_number', '').strip()

        if not email or not phone:
            messages.error(request, 'Email and Phone are required.')
            return redirect('user:edit_profile')

        if User.objects.filter(email=email).exclude(id=request.current_user.id).exists():
            messages.error(request, 'Email already registered.')
            return redirect('user:edit_profile')

        user = request.current_user
        user.email = email
        user.phone_number = phone
        user.save()
        
        request.session['user_email'] = email
        
        messages.success(request, '✅ Profile updated successfully!')
        return redirect('user:profile')

    return render(request, 'user/edit_profile.html', {
        'current_user': request.current_user
    })

@user_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        old_pass = request.POST.get('old_password', '')
        new_pass = request.POST.get('new_password', '')
        confirm_pass = request.POST.get('confirm_password', '')

        if not old_pass or not new_pass or not confirm_pass:
            messages.error(request, 'All fields are required.')
            return redirect('user:change_password')

        if not request.current_user.check_password(old_pass):
            messages.error(request, 'Current password is incorrect.')
            return redirect('user:change_password')

        if new_pass != confirm_pass:
            messages.error(request, 'New passwords do not match.')
            return redirect('user:change_password')

        if len(new_pass) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('user:change_password')

        request.current_user.set_password(new_pass)
        request.current_user.save()
        
        messages.success(request, 'Password changed successfully! Please login again.')
        request.session.flush()
        return redirect('guest:login')

    return render(request, 'user/change_password.html', {
        'current_user': request.current_user
    })

# ============================================
# 🛒 CART FUNCTIONALITY
# ============================================

@user_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # Check stock
    if product.stock < quantity:
        messages.error(request, f'Sorry, only {product.stock} items available')
        return redirect(request.META.get('HTTP_REFERER', 'user:home'))
    
    # Get or create cart item
    cart_item, created = Cart.objects.get_or_create(
        user=request.current_user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if product.stock >= new_quantity:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity to {new_quantity}')
        else:
            messages.error(request, f'Cannot add more. Only {product.stock} in stock')
    else:
        messages.success(request, f'✅ {product.name} added to cart!')
    
    return redirect(request.META.get('HTTP_REFERER', 'user:cart_view'))

@user_required
def cart_view(request):
    """View shopping cart"""
    cart_items = Cart.objects.filter(user=request.current_user).select_related('product')
    total_price = sum(item.item_total for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)
    
    return render(request, 'user/cart.html', {
        'current_user': request.current_user,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': cart_count,
    })

@user_required
def update_cart(request, cart_item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.current_user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'{product_name} removed from cart')
        elif cart_item.product.stock >= quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully')
        else:
            messages.error(request, f'Sorry, only {cart_item.product.stock} items available')
    
    return redirect('user:cart_view')

@user_required
def remove_from_cart(request, cart_item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.current_user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'✅ {product_name} removed from cart')
    return redirect('user:cart_view')

@user_required
def checkout(request):
    """Checkout page"""
    cart_items = Cart.objects.filter(user=request.current_user).select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('user:cart_view')
    
    total_price = sum(item.item_total for item in cart_items)
    
    # Get username from email (part before @)
    username = request.current_user.email.split('@')[0] if request.current_user.email else 'User'
    
    if request.method == 'POST':
        cart_items.delete()
        messages.success(request, '🎉 Order placed successfully! Thank you for shopping with CardNova.')
        return redirect('user:home')
    
    return render(request, 'user/checkout.html', {
        'current_user': request.current_user,
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_count': sum(item.quantity for item in cart_items),
        'username': username,  # Add this
    })

@user_required
def logout(request):
    """User logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('guest:home')