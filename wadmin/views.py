from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password
from guest.models import User, Admin
from .models import Category, Product, ProductImage
from functools import wraps

# ==========================================
# 🔐 Admin Access Decorator (DEFINE ONCE ONLY)
# ==========================================
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check session
        if request.session.get('user_type') != 'admin' or not request.session.get('aid'):
            messages.error(request, 'Admin access required. Please login.')
            return redirect('guest:login')
        
        # Safely fetch admin - handle if deleted from DB
        try:
            current_admin = Admin.objects.get(id=request.session['aid'])
            request.current_admin = current_admin  # Attach to request
        except Admin.DoesNotExist:
            # Session has invalid admin ID - clear and redirect
            request.session.flush()
            messages.error(request, 'Admin account not found. Please login again.')
            return redirect('guest:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==========================================
# 📦 Helper Functions
# ==========================================
def _get_categories():
    return Category.objects.all().order_by('name')

def _safe_form_data(request):
    return request.POST if request.method == 'POST' else {}

# ==========================================
# 📊 Dashboard & User Management
# ==========================================
@admin_required
def home(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'update_status' and user_id:
            new_status = request.POST.get('status')
            user = get_object_or_404(User, id=user_id)
            user.status = new_status
            user.save()
            messages.success(request, f'Status updated to {new_status} for {user.email}')
        elif action == 'delete' and user_id:
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, f'User {user.email} deleted')
        return redirect('wadmin:home')

    return render(request, 'wadmin/home.html', {
        'current_admin': request.current_admin,
        'stats': {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(status='active').count(),
            'pending_users': User.objects.filter(status='pending').count(),
            'total_admins': Admin.objects.count(),
        },
        'users': User.objects.all().order_by('-id')
    })

def logout(request):
    request.session.flush()
    messages.success(request, 'Admin logged out successfully.')
    return redirect('guest:login')

# ==========================================
# 👤 Profile Management
# ==========================================
@admin_required
def my_profile(request):
    """View admin profile"""
    admin = request.current_admin
    return render(request, 'wadmin/profile.html', {
        'current_admin': admin,
        'admin': admin
    })

@admin_required
def edit_profile(request):
    """Edit admin profile"""
    admin = request.current_admin
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        if not name:
            messages.error(request, 'Name is required.')
            return render(request, 'wadmin/edit_profile.html', {
                'current_admin': admin,
                'admin': admin,
                'form_data': request.POST
            })
        
        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'wadmin/edit_profile.html', {
                'current_admin': admin,
                'admin': admin,
                'form_data': request.POST
            })
        
        # Check if email already exists for another admin
        if Admin.objects.filter(email=email).exclude(id=admin.id).exists():
            messages.error(request, 'This email is already used by another admin.')
            return render(request, 'wadmin/edit_profile.html', {
                'current_admin': admin,
                'admin': admin,
                'form_data': request.POST
            })
        
        admin.name = name
        admin.email = email
        admin.phone = phone
        
        if request.FILES.get('profile_image'):
            admin.profile_image = request.FILES.get('profile_image')
        
        admin.save()
        request.session['admin_email'] = email
        
        messages.success(request, '✅ Profile updated successfully!')
        return redirect('wadmin:my_profile')
    
    return render(request, 'wadmin/edit_profile.html', {
        'current_admin': admin,
        'admin': admin
    })

@admin_required
def change_password(request):
    """Change admin password"""
    admin = request.current_admin
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not current_password:
            messages.error(request, 'Current password is required.')
            return render(request, 'wadmin/change_password.html', {'current_admin': admin})
        
        if not new_password:
            messages.error(request, 'New password is required.')
            return render(request, 'wadmin/change_password.html', {'current_admin': admin})
        
        if len(new_password) < 6:
            messages.error(request, 'New password must be at least 6 characters long.')
            return render(request, 'wadmin/change_password.html', {'current_admin': admin})
        
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return render(request, 'wadmin/change_password.html', {'current_admin': admin})
        
        if not check_password(current_password, admin.password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'wadmin/change_password.html', {'current_admin': admin})
        
        admin.password = make_password(new_password)
        admin.save()
        
        messages.success(request, '✅ Password changed successfully! Please login again.')
        request.session.flush()
        return redirect('guest:login')
    
    return render(request, 'wadmin/change_password.html', {'current_admin': admin})

# ==========================================
# 🏷️ Category Management
# ==========================================
@admin_required
def manage_categories(request):
    return render(request, 'wadmin/categories.html', {
        'current_admin': request.current_admin,
        'categories': Category.objects.all().order_by('-created_at')
    })

@admin_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Category name is required.')
            return render(request, 'wadmin/category_form.html', {
                'current_admin': request.current_admin,
                'form_data': request.POST
            })

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Category "{name}" already exists!')
            return render(request, 'wadmin/category_form.html', {
                'current_admin': request.current_admin,
                'form_data': request.POST
            })

        slug = slugify(name)
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f'A category with similar name "{name}" already exists!')
            return render(request, 'wadmin/category_form.html', {
                'current_admin': request.current_admin,
                'form_data': request.POST
            })

        Category.objects.create(
            name=name,
            slug=slug,
            icon=icon,
            is_active=is_active
        )
        messages.success(request, f'✅ Category "{name}" created successfully!')
        return redirect('wadmin:manage_categories')

    return render(request, 'wadmin/category_form.html', {
        'current_admin': request.current_admin,
        'form_data': {}
    })

@admin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not name:
            messages.error(request, 'Category name is required.')
        elif Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            category.name = name
            category.slug = slugify(name)
            category.icon = icon
            category.is_active = is_active
            category.save()
            messages.success(request, f'✅ Category "{name}" updated successfully!')
            return redirect('wadmin:manage_categories')

    return render(request, 'wadmin/category_form.html', {
        'current_admin': request.current_admin,
        'category': category,
        'form_data': _safe_form_data(request)
    })

@admin_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        messages.success(request, f'✅ Category "{category.name}" deleted.')
    return redirect('wadmin:manage_categories')

# ==========================================
# 🃏 Product Management with Multiple Images
# ==========================================
@admin_required
def manage_products(request):
    return render(request, 'wadmin/products.html', {
        'current_admin': request.current_admin,
        'products': Product.objects.select_related('category').all()
    })

@admin_required
def add_product(request):
    active_categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category') or None
        description = request.POST.get('description', '').strip()
        release_date = request.POST.get('release_date') or None
        price = request.POST.get('price')
        sale_price = request.POST.get('sale_price') or None
        stock = request.POST.get('stock', 0)
        is_active = request.POST.get('is_active') == 'on'
        main_image = request.FILES.get('image')
        additional_images = request.FILES.getlist('additional_images')

        if not name:
            messages.error(request, 'Product name is required.')
            return render(request, 'wadmin/product_form.html', {
                'current_admin': request.current_admin,
                'categories': active_categories,
                'form_data': request.POST
            })

        if not price:
            messages.error(request, 'Product price is required.')
            return render(request, 'wadmin/product_form.html', {
                'current_admin': request.current_admin,
                'categories': active_categories,
                'form_data': request.POST
            })

        if category_id and Product.objects.filter(
            name__iexact=name, 
            category_id=category_id
        ).exists():
            messages.error(request, f'Product "{name}" already exists in this category!')
            return render(request, 'wadmin/product_form.html', {
                'current_admin': request.current_admin,
                'categories': active_categories,
                'form_data': request.POST
            })

        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        product = Product.objects.create(
            name=name,
            slug=slug,
            category_id=category_id if category_id else None,
            description=description,
            release_date=release_date or None,
            price=price,
            sale_price=sale_price if sale_price else None,
            stock=stock,
            image=main_image,
            is_active=is_active
        )
        
        for idx, img in enumerate(additional_images):
            ProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(idx == 0 and not main_image),
                order=idx
            )
        
        image_count = len(additional_images)
        messages.success(request, f'✅ Product "{name}" created successfully with {image_count} additional image(s)!')
        return redirect('wadmin:manage_products')

    return render(request, 'wadmin/product_form.html', {
        'current_admin': request.current_admin,
        'categories': active_categories,
        'form_data': {}
    })

@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = product.images.all()
    active_categories = Category.objects.filter(is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category') or None
        description = request.POST.get('description', '').strip()
        release_date = request.POST.get('release_date') or None
        price = request.POST.get('price')
        sale_price = request.POST.get('sale_price') or None
        stock = request.POST.get('stock', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if category_id and Product.objects.filter(
            name__iexact=name,
            category_id=category_id
        ).exclude(id=product_id).exists():
            messages.error(request, f'Product "{name}" already exists in this category!')
            return render(request, 'wadmin/product_form.html', {
                'current_admin': request.current_admin,
                'categories': active_categories,
                'product': product,
                'product_images': product_images,
                'form_data': request.POST
            })
        
        if product.name.lower() != name.lower():
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(id=product_id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = slug
        
        product.name = name
        product.category_id = category_id if category_id else None
        product.description = description
        product.release_date = release_date or None
        product.price = price
        product.sale_price = sale_price or None
        product.stock = stock
        product.is_active = is_active
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        
        additional_images = request.FILES.getlist('additional_images')
        current_image_count = product.images.count()
        
        for idx, img in enumerate(additional_images):
            ProductImage.objects.create(
                product=product,
                image=img,
                order=current_image_count + idx
            )
        
        if additional_images:
            messages.success(request, f'✅ Product "{product.name}" updated with {len(additional_images)} new image(s)!')
        else:
            messages.success(request, f'✅ Product "{product.name}" updated successfully!')
        
        return redirect('wadmin:manage_products')

    return render(request, 'wadmin/product_form.html', {
        'current_admin': request.current_admin,
        'categories': active_categories,
        'product': product,
        'product_images': product_images,
        'form_data': {}
    })

@admin_required
def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'✅ Product "{product_name}" deleted successfully.')
    return redirect('wadmin:manage_products')

# ==========================================
# 🖼️ Product Image Management
# ==========================================
@admin_required
def delete_product_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(ProductImage, id=image_id)
        product_id = image.product.id
        image.delete()
        messages.success(request, '✅ Image deleted successfully.')
    return redirect('wadmin:edit_product', product_id=product_id)

@admin_required
def set_primary_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(ProductImage, id=image_id)
        image.is_primary = True
        image.save()
        messages.success(request, '✅ Primary image updated successfully.')
    return redirect('wadmin:edit_product', product_id=image.product.id)

@admin_required
def reorder_images(request, product_id):
    if request.method == 'POST':
        order_data = request.POST.getlist('image_order[]')
        for idx, image_id in enumerate(order_data):
            ProductImage.objects.filter(id=image_id).update(order=idx)
        messages.success(request, '✅ Image order updated successfully.')
    return redirect('wadmin:edit_product', product_id=product_id)