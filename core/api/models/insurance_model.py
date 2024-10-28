from django.db import models

class Insurance(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    insurance_company = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    coverage_details = models.TextField()
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claim_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
