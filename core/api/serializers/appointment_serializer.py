# from api.models.patient_model import Patient, Bed
# from api.models.appointment_model import Appointment
# from api.models.surgery_model import OperationTheater, Surgery

# from api.serializers.staff_serializer import DoctorSerializer
# from api.serializers.patient_serializer import PatientSerializer
# from rest_framework import serializers
# from django.utils import timezone
# from datetime import timedelta
# from django.core.cache import cache


# class AppointmentSerializer(serializers.ModelSerializer):
#     patient_details = PatientSerializer(source='patient', read_only=True)
#     doctor_details = DoctorSerializer(source='doctor', read_only=True)
#     estimated_duration = serializers.SerializerMethodField()
#     priority_level = serializers.SerializerMethodField()

#     class Meta:
#         model = Appointment
#         fields = '__all__'
#         read_only_fields = ('is_confirmed', 'status')

#     def get_estimated_duration(self, obj):
#         # Calculate based on reason and patient history
#         base_duration = 30  # Base duration in minutes
#         if 'surgery' in obj.reason.lower():
#             base_duration += 30
#         if 'emergency' in obj.reason.lower():
#             base_duration -= 10
#         return base_duration

#     def get_priority_level(self, obj):
#         priority = 1  # Normal priority
        
#         # Increase priority for specific conditions
#         if 'emergency' in obj.reason.lower():
#             priority += 3
#         if obj.patient.admitted:
#             priority += 1
#         if 'urgent' in obj.reason.lower():
#             priority += 2
            
#         return min(priority, 5)  # Max priority of 5

#     def validate(self, data):
#         if data['appointment_time'] < timezone.now():
#             raise serializers.ValidationError("Cannot schedule appointments in the past.")

#         # Check doctor availability
#         doctor_busy = self._check_doctor_availability(
#             data['doctor'],
#             data['appointment_time']
#         )
#         if doctor_busy:
#             raise serializers.ValidationError("Doctor is not available at this time.")

#         # Check patient availability
#         patient_busy = self._check_patient_availability(
#             data['patient'],
#             data['appointment_time']
#         )
#         if patient_busy:
#             raise serializers.ValidationError("Patient has another appointment at this time.")

#         return data

#     def _check_doctor_availability(self, doctor, appointment_time):
#         # Check appointments
#         existing_appointment = Appointment.objects.filter(
#             doctor=doctor,
#             appointment_time__range=(
#                 appointment_time - timedelta(minutes=30),
#                 appointment_time + timedelta(minutes=30)
#             ),
#             status__in=['confirmed', 'in_progress']
#         ).exists()

#         # Check surgeries
#         existing_surgery = Surgery.objects.filter(
#             primary_surgeon=doctor,
#             scheduled_date__range=(
#                 appointment_time - timedelta(hours=2),
#                 appointment_time + timedelta(hours=2)
#             ),
#             status__in=['scheduled', 'in_progress']
#         ).exists()

#         return existing_appointment or existing_surgery

#     def _check_patient_availability(self, patient, appointment_time):
#         return Appointment.objects.filter(
#             patient=patient,
#             appointment_time__range=(
#                 appointment_time - timedelta(minutes=30),
#                 appointment_time + timedelta(minutes=30)
#             ),
#             status__in=['confirmed', 'in_progress']
#         ).exists()