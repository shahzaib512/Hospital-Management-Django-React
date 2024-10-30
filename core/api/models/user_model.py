# users/models.py
from django.db import models
from .abstract_user import AbstractUser
from .branch_model import Branch
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class User(AbstractUser):
    # Enhanced Role choices with descriptions
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    # Gender choices
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Enhanced fields with validators and better organization
    full_name = models.CharField(
        _('Full Name'),
        max_length=255,
        help_text=_('Enter your full name as per official documents')
    )

    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        unique=True,
        help_text=_('Enter a valid phone number')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='guest',
        help_text=_('Select user role')
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    # Additional base fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def get_full_name(self):
        return self.full_name

    def get_role_display_name(self):
        return dict(self.ROLE_CHOICES).get(self.role, '')

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_patient(self):
        return self.role == 'patient'

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Basic Information
    profile_picture = models.ImageField(
        upload_to='profiles/images/%Y/%m/',
        null=True,
        blank=True
    )
    gender = models.CharField(
        max_length=1,
        choices=User.GENDER_CHOICES,
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    # Contact Information
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, null=True, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, null=True, blank=True)

    # Professional Information (for staff/doctors)
    designation = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    license_number = models.CharField(max_length=100, null=True, blank=True)

    # System Information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return f"{self.user.full_name}'s Profile"

    def save(self, *args, **kwargs):
        # Check if profile is complete based on user role
        if self.user.role == 'doctor':
            self.is_complete = all([
                self.gender,
                self.qualification,
                self.specialization,
                self.license_number
            ])
        elif self.user.role == 'patient':
            self.is_complete = all([
                self.gender,
                self.date_of_birth,
                self.blood_group,
                self.emergency_contact_name,
                self.emergency_contact_phone
            ])
        super().save(*args, **kwargs)

# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()