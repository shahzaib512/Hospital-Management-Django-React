from rest_framework import viewsets, status 
from rest_framework.response import Response
from rest_framework.decorators import action 
from django.utils import timezone 
from django.core.cache import cache 
from django.db.models import Count, F, Q, Case, When, Value, CharField

from api.models.patient_model import Patient, Bed  
from api.models.appointment_model import Appointment
from api.models.surgery_model import OperationTheater, Surgery
from api.serializers.patient_serializer import PatientSerializer, BedSerializer


class BedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Bed data with enhanced filtering and caching.
    """
    queryset = Bed.objects.all()
    serializer_class = BedSerializer

    def get_queryset(self):
        # Optimize queryset by prefetching related data and adding conditional annotations
        return Bed.objects.annotate(
            occupied=Case(
                When(patient__admitted=True, then=Value('Occupied')),
                default=Value('Available'),
                output_field=CharField()
            )
        ).prefetch_related('patient_set')

    @action(detail=True, methods=['get'])
    def current_patient(self, request, pk=None):
        bed = self.get_object()
        current_patient = Patient.objects.filter(bed=bed, admitted=True).first()
        data = {'current_patient': current_patient.user.get_full_name() if current_patient else None}
        return Response(data)

    @action(detail=True, methods=['get'])
    def occupancy_history(self, request, pk=None):
        bed = self.get_object()
        history = bed.patient_set.filter(admitted=False).values(
            patient_name=F('user__full_name'),
            admitted_date=F('admitted_date'),
            discharge_date=F('discharged_date')
        )
        return Response({'occupancy_history': list(history)})


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Patient data with advanced filtering and caching.
    """
    queryset = Patient.objects.select_related('user', 'bed').all()
    serializer_class = PatientSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f"patient_{instance.id}_data"
        
        # Retrieve or cache data for efficiency
        cached_data = cache.get(cache_key)
        if not cached_data:
            serializer = self.get_serializer(instance)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, timeout=300)
        return Response(cached_data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        patient = self.get_object()
        # Filter upcoming appointments and prefetch related doctor data
        appointments = patient.appointment_set.filter(
            appointment_time__gte=timezone.now()
        ).select_related('doctor', 'doctor__user').only(
            'appointment_time', 'reason', 'status', 'doctor__user__full_name'
        ).order_by('-appointment_time')[:5]

        return Response({'appointments': appointments})

    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        patient = self.get_object()
        # Filter and fetch related surgeries and appointments for medical history
        surgeries = Surgery.objects.filter(patient=patient).values(
            'surgery_type', 'scheduled_date', 'complications'
        )
        appointments = Appointment.objects.filter(patient=patient).values(
            'appointment_time', 'reason', 'status'
        )
        return Response({
            'medical_history': {
                'surgeries': list(surgeries),
                'appointments': list(appointments)
            }
        })

    @action(detail=True, methods=['get'])
    def upcoming_surgeries(self, request, pk=None):
        patient = self.get_object()
        # Filter upcoming surgeries and use select_related for optimized data retrieval
        upcoming_surgeries = Surgery.objects.filter(
            patient=patient,
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).select_related('primary_surgeon', 'operation_theater')

        # Annotate with additional fields if necessary
        annotated_surgeries = upcoming_surgeries.annotate(
            surgeon_name=F('primary_surgeon__user__full_name'),
            theater_name=F('operation_theater__name')
        ).only('surgery_type', 'scheduled_date', 'surgeon_name', 'theater_name')

        return Response({'upcoming_surgeries': annotated_surgeries})

    @action(detail=True, methods=['get'])
    def billing_summary(self, request, pk=None):
        patient = self.get_object()
        # Aggregate total bills for the patient using related data
        total_bills = patient.billing_set.aggregate(total=Sum('amount'))
        return Response({'total_bills': total_bills['total']})
    

    
        