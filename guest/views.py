from django.shortcuts import render, redirect, get_object_or_404  # ✅ Add get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import User, Admin
from wadmin.models import Product, Category

def login(request):
    """Unified login for both User and Admin"""
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Email and Password are required.')
            return render(request, 'guest/login.html')

        # Check User table first
        user = User.objects.filter(email=email).first()
        
        if user:
            password_valid = check_password(password, user.password)
            
            if password_valid:
                if user.status == 'active':
                    request.session['uid'] = user.id
                    request.session['user_id'] = user.id
                    request.session['user_email'] = user.email
                    request.session['user_type'] = 'user'
                    messages.success(request, f'Welcome back, {user.email}!')
                    return redirect('user:home')
                elif user.status == 'pending':
                    messages.error(request, 'Your account is pending verification.')
                else:
                    messages.error(request, 'Your account has been restricted.')
                return render(request, 'guest/login.html')
            else:
                messages.error(request, 'Invalid password.')
                return render(request, 'guest/login.html')

        # Check Admin table
        admin = Admin.objects.filter(email=email).first()
        
        if admin:
            password_valid = check_password(password, admin.password)
            
            if password_valid:
                if admin.status == 'active':
                    request.session['aid'] = admin.id
                    request.session['admin_id'] = admin.id
                    request.session['admin_email'] = admin.email
                    request.session['user_type'] = 'admin'
                    messages.success(request, f'Admin access granted, {admin.email}!')
                    return redirect('wadmin:home')
                else:
                    messages.error(request, 'Admin account is inactive.')
            else:
                messages.error(request, 'Invalid password.')
            return render(request, 'guest/login.html')

        messages.error(request, 'Invalid email or password.')
        return render(request, 'guest/login.html')

    return render(request, 'guest/login.html')


def register_view(request):
    """Guest registration - email, phone, password required"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not email or not phone or not password:
            messages.error(request, 'Email, Phone Number, and Password are required.')
            return render(request, 'guest/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'guest/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'guest/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'guest/register.html')
        
        User.objects.create(
            email=email,
            phone_number=phone,
            password=make_password(password),
            status='active'
        )
        messages.success(request, 'Account created! Please login.')
        return redirect('guest:login')
    
    return render(request, 'guest/register.html')


def logout(request):
    """Clear session for both user and admin"""
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('guest:home')


def home(request):
    """Home page for guests (storefront)"""
    user_id = request.session.get('uid') or request.session.get('user_id')
    admin_id = request.session.get('aid') or request.session.get('admin_id')
    
    current_user = None
    current_admin = None
    
    if user_id:
        try:
            current_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    if admin_id:
        try:
            current_admin = Admin.objects.get(id=admin_id)
        except Admin.DoesNotExist:
            pass
    
    # Get products for display
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'guest/home.html', {
        'current_user': current_user,
        'current_admin': current_admin,
        'products': products,
        'categories': categories,
    })


def product_list(request):
    """View all products with filtering"""
    from django.shortcuts import get_object_or_404  # Already imported at top
    
    user_id = request.session.get('uid') or request.session.get('user_id')
    admin_id = request.session.get('aid') or request.session.get('admin_id')
    
    current_user = None
    current_admin = None
    
    if user_id:
        try:
            current_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    if admin_id:
        try:
            current_admin = Admin.objects.get(id=admin_id)
        except Admin.DoesNotExist:
            pass
    
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
    # Sort options
    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')
    
    return render(request, 'guest/product_list.html', {
        'current_user': current_user,
        'current_admin': current_admin,
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search,
        'sort_by': sort,
    })


def product_detail(request, product_id):
    """View single product details"""
    from django.shortcuts import get_object_or_404  # Already imported at top
    
    user_id = request.session.get('uid') or request.session.get('user_id')
    admin_id = request.session.get('aid') or request.session.get('admin_id')
    
    current_user = None
    current_admin = None
    
    if user_id:
        try:
            current_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    if admin_id:
        try:
            current_admin = Admin.objects.get(id=admin_id)
        except Admin.DoesNotExist:
            pass
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    product_images = product.images.all()
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product_id)[:4]
    
    return render(request, 'guest/product_detail.html', {
        'current_user': current_user,
        'current_admin': current_admin,
        'product': product,
        'product_images': product_images,
        'related_products': related_products,
    })