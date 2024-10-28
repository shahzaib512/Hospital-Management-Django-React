from django.db import models

class OperationTheater(models.Model):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    floor = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    last_sanitized = models.DateTimeField()
    equipment_status = models.TextField()

class Surgery(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    operation_theater = models.ForeignKey(OperationTheater, on_delete=models.CASCADE)
    primary_surgeon = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='primary_surgeries')
    assisting_surgeons = models.ManyToManyField('Doctor', related_name='assisting_surgeries')
    surgery_type = models.CharField(max_length=255)
    scheduled_date = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    pre_op_notes = models.TextField()
    post_op_notes = models.TextField()
    complications = models.TextField(blank=True)
    anesthesia_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
