"""
URL configuration for CardNova project.
Gaming Cards & Collectibles Store
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# ==========================================
# Custom Error Handlers (Optional)
# ==========================================
def custom_404(request, exception):
    """Custom 404 page"""
    return HttpResponse(
        "<h1>404 - Page Not Found</h1><p>The card you're looking for doesn't exist.</p><a href='/'>← Back to Home</a>",
        status=404
    )

def custom_500(request):
    """Custom 500 page"""
    return HttpResponse(
        "<h1>500 - Server Error</h1><p>Something went wrong. Our team is fixing it.</p><a href='/'>← Back to Home</a>",
        status=500
    )

# Assign handlers
handler404 = 'config.urls.custom_404'
handler500 = 'config.urls.custom_500'

# ==========================================
# Main URL Patterns
# ==========================================
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('guest.urls')),           # Guest: /, /login/, /register/
    path('user/', include('user.urls')),       # User: /user/, /user/profile/
    path('wadmin/', include('wadmin.urls')),   # Admin: /wadmin/, /wadmin/categories/
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ==========================================
# Serve Media Files in Development
# ==========================================
# This allows uploaded product images to be served during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Optional: Serve static files with Django during development (if not using whitenoise)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==========================================
# Production Notes
# ==========================================
"""
In production:
1. Set DEBUG = False in settings.py
2. Use a proper web server (Nginx/Apache) to serve STATIC_ROOT and MEDIA_ROOT
3. Remove the static() URLs above or guard them with if not settings.DEBUG
4. Add your domain to ALLOWED_HOSTS in settings.py
5. Set CSRF_COOKIE_SECURE = True and SESSION_COOKIE_SECURE = True
"""