# models/admin.py

from django.contrib import admin
from .models import User, Branch, Doctor, Nurse, Receptionist, Patient, Appointment, MedicalRecord, Prescription, Laboratory, LabTest, OperationTheater, Surgery, BloodInventory, BloodDonation, Billing, Insurance, Department

# Register your models here.
admin.site.register(User)
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Nurse)
admin.site.register(Receptionist)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(Prescription)
admin.site.register(Laboratory)
admin.site.register(LabTest)
admin.site.register(OperationTheater)
admin.site.register(Surgery)
admin.site.register(BloodInventory)
admin.site.register(BloodDonation)
admin.site.register(Billing)
admin.site.register(Insurance)
