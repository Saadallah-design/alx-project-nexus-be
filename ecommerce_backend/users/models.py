# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from uuid import uuid4

# Fixing the UserManager.create_superuser() missing 1 required positional argument: 'username' error
# by creating a new class called CustomUserManager.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    # We inherit from Django's AbstractUser class, which provides all the standard fields necessary for authentication 
    # (e.g., password, is_active, is_staff, permissions, etc.). We don't have to write them ourselves.
    email = models.EmailField(unique=True, null=False, blank=False)
    #  unique=True, ensuring every user has a unique email. This is the primary login identifier for our API.

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # Instead of using the default sequential integer primary key (SERIAL), 
    # we use a UUID (Universally Unique Identifier). This is a best practice for API backends 
    # because UUIDs are harder to guess than sequential IDs, improving security and better supporting horizontal scaling.
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    # FIX: Activates the custom manager
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    # This line explicitly tells Django's authentication system to use the email field 
    # instead of the default username field for login (which is common for modern APIs).
    REQUIRED_FIELDS = ['first_name', 'last_name']

    
    
    def __str__(self):
        return self.email
    
# This code block used defines our main user table, 
# which is critical for authentication (JWT), cart ownership, wishlist ownership, and order tracking.