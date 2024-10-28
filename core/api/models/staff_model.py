from django.db import models
from django.utils.timezone import now

class Doctor(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    specialization = models.CharField(max_length=255)
    qualifications = models.TextField()
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    is_available = models.BooleanField(default=True)

class Nurse(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    shift_start = models.TimeField()
    shift_end = models.TimeField()

class Receptionist(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True)
