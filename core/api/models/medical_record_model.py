from django.db import models
from django.utils.timezone import now

class MedicalRecord(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    visit_date = models.DateField(default=now)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    notes = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
