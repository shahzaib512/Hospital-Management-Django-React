from django.db import models
from .abstract_user import AbstractUser
from .branch_model import Branch

class User(AbstractUser):
    # Role choices for the user
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
    ]

    # Additional fields
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=12, blank=True, null=True)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Override properties from AbstractUser
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    # You can add custom methods here if needed
