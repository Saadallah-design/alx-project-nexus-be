# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4

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
    
    USERNAME_FIELD = 'email'
    # This line explicitly tells Django's authentication system to use the email field 
    # instead of the default username field for login (which is common for modern APIs).
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
# This code block used defines our main user table, 
# which is critical for authentication (JWT), cart ownership, wishlist ownership, and order tracking.