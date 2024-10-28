from django.db import models
from django.utils.timezone import now

class Prescription(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    medical_record = models.ForeignKey('MedicalRecord', on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50)
    instructions = models.TextField()
    prescribed_date = models.DateField(default=now)
