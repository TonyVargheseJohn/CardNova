from django.db import models

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50)
    password = models.CharField(max_length=255)  # Increased for hashed passwords
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'tbl_user'

    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the raw password matches the hashed password"""
        return check_password(raw_password, self.password)
    


from django.utils import timezone

class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='admin_profiles/', null=True, blank=True)
    status = models.CharField(max_length=20, default='active')
    role = models.CharField(max_length=50, default='superadmin')
    created_at = models.DateTimeField(default=timezone.now)  # Use default instead of auto_now_add
    updated_at = models.DateTimeField(auto_now=True, null=True)  # Keep auto_now

    class Meta:
        db_table = 'tbl_admin'

    def __str__(self):
        return self.email