from django.db import models

class Billing(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    appointment = models.ForeignKey('Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('partial', 'Partial')
    ], default='unpaid')
    payment_date = models.DateTimeField(blank=True, null=True)