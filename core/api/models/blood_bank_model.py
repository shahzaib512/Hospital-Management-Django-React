from django.db import models

class BloodInventory(models.Model):
    blood_group = models.CharField(max_length=3)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    units_available = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField()
    storage_location = models.CharField(max_length=100)

class BloodDonation(models.Model):
    donor_name = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=3)
    donation_date = models.DateTimeField(auto_now_add=True)
    units_donated = models.IntegerField()
    medical_history = models.TextField()
    is_eligible = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15)