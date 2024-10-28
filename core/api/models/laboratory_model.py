from django.db import models

class Laboratory(models.Model):
    name = models.CharField(max_length=255)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    lab_type = models.CharField(max_length=100)
    capacity = models.IntegerField()
    is_operational = models.BooleanField(default=True)

class LabTest(models.Model):
    name = models.CharField(max_length=255)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    preparation_instructions = models.TextField()