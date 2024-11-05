# from api.models.patient_model import Patient, Bed
# from api.models.appointment_model import Appointment
# from api.models.staff_model import Doctor, Nurse
# from api.models.surgery_model import OperationTheater, Surgery
# from api.serializers.appointment_serializer import AppointmentSerializer
# from api.serializers.surgery_serializer import SurgerySerializer
# from rest_framework import serializers
# from django.utils import timezone
# from datetime import timedelta
# from django.core.cache import cache


# class CachedSerializerMixin:
#     """
#     Mixin to add caching capabilities to serializers
#     """
#     @property
#     def cache_key(self):
#         return f"{self.Meta.model.__name__}_{self.instance.id}_serialized"

#     def to_representation(self, instance):
#         self.instance = instance
#         cached_data = cache.get(self.cache_key)
#         if cached_data is None:
#             cached_data = super().to_representation(instance)
#             cache.set(self.cache_key, cached_data, timeout=300)  # 5 minutes cache
#         return cached_data


# class DoctorSerializer(CachedSerializerMixin, serializers.ModelSerializer):
#     efficiency_rating = serializers.SerializerMethodField()
#     current_workload = serializers.SerializerMethodField()
#     schedule_conflicts = serializers.SerializerMethodField()
#     expertise_areas = serializers.ListField(write_only=True, required=False)

#     class Meta:
#         model = Doctor
#         fields = '__all__'
#         extra_kwargs = {
#             'user': {'read_only': True}
#         }

#     def get_efficiency_rating(self, obj):
#         completed_appointments = Appointment.objects.filter(
#             doctor=obj,
#             status='completed'
#         ).count()
#         cancelled_appointments = Appointment.objects.filter(
#             doctor=obj,
#             status='cancelled'
#         ).count()
        
#         if completed_appointments + cancelled_appointments == 0:
#             return None
            
#         return (completed_appointments / (completed_appointments + cancelled_appointments)) * 100

#     def get_current_workload(self, obj):
#         today = timezone.now()
#         current_appointments = Appointment.objects.filter(
#             doctor=obj,
#             appointment_time__date=today.date(),
#             status__in=['confirmed', 'in_progress']
#         ).count()
        
#         current_surgeries = Surgery.objects.filter(
#             primary_surgeon=obj,
#             scheduled_date__date=today.date(),
#             status__in=['scheduled', 'in_progress']
#         ).count()
        
#         return {
#             'appointments': current_appointments,
#             'surgeries': current_surgeries,
#             'total_workload': current_appointments + (current_surgeries * 3)  # Surgeries weighted more
#         }

#     def get_schedule_conflicts(self, obj):
#         conflicts = []
#         upcoming_schedule = list(Appointment.objects.filter(
#             doctor=obj,
#             appointment_time__gte=timezone.now(),
#             status='confirmed'
#         ).order_by('appointment_time'))
        
#         for i in range(len(upcoming_schedule) - 1):
#             current = upcoming_schedule[i]
#             next_appointment = upcoming_schedule[i + 1]
#             time_difference = (next_appointment.appointment_time - current.appointment_time).total_seconds() / 60
            
#             if time_difference < 30:  # Less than 30 minutes between appointments
#                 conflicts.append({
#                     'first_appointment': current.id,
#                     'second_appointment': next_appointment.id,
#                     'time_difference': time_difference
#                 })
        
#         return conflicts
        

