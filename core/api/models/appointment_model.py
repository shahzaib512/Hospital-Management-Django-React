from django.db import models

class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], default='pending')
    reason = models.TextField()
    is_confirmed = models.BooleanField(default=False)