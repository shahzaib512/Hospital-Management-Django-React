from django.db import models

class Bed(models.Model):
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.number

class Patient(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3)
    date_of_birth = models.DateField()
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    admitted = models.BooleanField(default=False)
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True)