from api.models.patient_model import Patient, Bed
from api.models.appointment_model import Appointment
from api.models.surgery_model import OperationTheater, Surgery
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

class CachedSerializerMixin:
    """
    Mixin to add caching capabilities to serializers
    """
    @property
    def cache_key(self):
        return f"{self.Meta.model.__name__}_{self.instance.id}_serialized"

    def to_representation(self, instance):
        self.instance = instance
        cached_data = cache.get(self.cache_key)
        if cached_data is None:
            cached_data = super().to_representation(instance)
            cache.set(self.cache_key, cached_data, timeout=300)  # 5 minutes cache
        return cached_data

class BedSerializer(CachedSerializerMixin, serializers.ModelSerializer):
    current_patient_name = serializers.SerializerMethodField()
    occupancy_history = serializers.SerializerMethodField()

    class Meta:
        model = Bed
        fields = '__all__'

    def get_current_patient_name(self, obj):
        current_patient = Patient.objects.filter(bed=obj, admitted=True).first()
        return current_patient.user.get_full_name() if current_patient else None

    def get_occupancy_history(self, obj):
        return Patient.objects.filter(
            bed=obj
        ).values('user__full_name', 'admitted', 'date_of_birth')

class PatientSerializer(CachedSerializerMixin, serializers.ModelSerializer):
    bed = BedSerializer(read_only=True)
    appointments = serializers.SerializerMethodField()
    medical_history = serializers.SerializerMethodField()
    upcoming_surgeries = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    total_bills = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'emergency_contact': {'required': True}
        }

    def get_age(self, obj):
        return (timezone.now().date() - obj.date_of_birth).days // 365

    def get_appointments(self, obj):
        return Appointment.objects.filter(patient=obj).select_related(
            'doctor', 'doctor__user'
        ).order_by('-appointment_time')[:5]

    def get_medical_history(self, obj):
        surgeries = Surgery.objects.filter(patient=obj).values(
            'surgery_type', 'scheduled_date', 'complications'
        )
        appointments = Appointment.objects.filter(patient=obj).values(
            'appointment_time', 'reason', 'status'
        )
        return {
            'surgeries': surgeries,
            'appointments': appointments
        }

    def get_upcoming_surgeries(self, obj):
        return Surgery.objects.filter(
            patient=obj,
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).select_related('primary_surgeon', 'operation_theater')

    def get_total_bills(self, obj):
        # Implement billing logic here
        pass

    def validate(self, data):
        if data.get('admitted') and not data.get('bed'):
            raise serializers.ValidationError(
                "Bed assignment is required for admitted patients"
            )
        return data

