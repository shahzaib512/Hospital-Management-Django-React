# from api.models.patient_model import Patient, Bed
# from api.models.appointment_model import Appointment
# from api.models.surgery_model import OperationTheater, Surgery
# from api.serializers.staff_serializer import DoctorSerializer
# from rest_framework import serializers
# from django.utils import timezone
# from datetime import timedelta
# from django.core.cache import cache

# class SurgerySerializer(serializers.ModelSerializer):
#     primary_surgeon_details = DoctorSerializer(source='primary_surgeon', read_only=True)
#     operation_theater_details = serializers.SerializerMethodField()
#     risk_assessment = serializers.SerializerMethodField()
#     required_resources = serializers.SerializerMethodField()
#     estimated_duration = serializers.SerializerMethodField()

#     class Meta:
#         model = Surgery
#         fields = '__all__'

#     def get_operation_theater_details(self, obj):
#         return {
#             'name': obj.operation_theater.name,
#             'floor': obj.operation_theater.floor,
#             'last_sanitized': obj.operation_theater.last_sanitized,
#             'equipment_status': obj.operation_theater.equipment_status,
#             'upcoming_surgeries': Surgery.objects.filter(
#                 operation_theater=obj.operation_theater,
#                 scheduled_date__gte=timezone.now()
#             ).count()
#         }

#     def get_risk_assessment(self, obj):
#         risk_factors = []
#         risk_level = 'LOW'
        
#         # Check patient history
#         patient_surgeries = Surgery.objects.filter(
#             patient=obj.patient,
#             status='completed'
#         ).count()
        
#         if patient_surgeries > 3:
#             risk_factors.append('Multiple previous surgeries')
#             risk_level = 'MEDIUM'
            
#         if 'complications' in obj.pre_op_notes.lower():
#             risk_factors.append('Pre-operation complications noted')
#             risk_level = 'HIGH'
            
#         # Check surgery type specific risks
#         high_risk_types = ['cardiac', 'neural', 'emergency']
#         if any(risk_type in obj.surgery_type.lower() for risk_type in high_risk_types):
#             risk_factors.append('High-risk surgery type')
#             risk_level = 'HIGH'
            
#         return {
#             'risk_level': risk_level,
#             'risk_factors': risk_factors,
#             'recommendations': self._get_risk_recommendations(risk_level)
#         }

#     def _get_risk_recommendations(self, risk_level):
#         recommendations = {
#             'LOW': ['Standard monitoring', 'Regular checks'],
#             'MEDIUM': ['Increased monitoring', 'Backup equipment ready', 'Additional staff on standby'],
#             'HIGH': ['Continuous monitoring', 'Specialist consultation required', 'ICU booking recommended']
#         }
#         return recommendations.get(risk_level, [])

#     def get_required_resources(self, obj):
#         # Define base resources needed for all surgeries
#         base_resources = {
#             'medical_staff': {
#                 'surgeons': 1,
#                 'nurses': 2,
#                 'anesthesiologists': 1
#             },
#             'equipment': ['Basic surgical kit', 'Monitoring equipment'],
#             'medications': ['Anesthesia', 'Antibiotics']
#         }
        
#         # Add surgery-specific resources
#         if 'cardiac' in obj.surgery_type.lower():
#             base_resources['equipment'].extend(['Heart-lung machine', 'Cardiac monitors'])
#             base_resources['medical_staff']['nurses'] += 1
            
#         return base_resources

#     def get_estimated_duration(self, obj):
#         # Base duration in minutes
#         base_duration = {
#             'minor': 60,
#             'major': 180,
#             'complex': 300
#         }
        
#         # Determine complexity
#         complexity = 'minor'
#         if any(word in obj.surgery_type.lower() for word in ['cardiac', 'neural', 'transplant']):
#             complexity = 'complex'
#         elif any(word in obj.surgery_type.lower() for word in ['major', 'extensive']):
#             complexity = 'major'
            
#         return base_duration[complexity]

#     def validate(self, data):
#         super().validate(data)
        
#         # Validate operation theater availability
#         if not self._validate_operation_theater(data):
#             raise serializers.ValidationError(
#                 "Operation theater is not available or not properly sanitized"
#             )
            
#         # Validate surgical team availability
#         if not self._validate_surgical_team(data):
#             raise serializers.ValidationError(
#                 "One or more surgical team members are not available"
#             )
            
#         # Validate patient readiness
#         if not self._validate_patient_readiness(data):
#             raise serializers.ValidationError(
#                 "Patient is not ready for surgery"
#             )
            
#         return data

#     def _validate_operation_theater(self, data):
#         theater = data['operation_theater']
#         surgery_date = data['scheduled_date']
        
#         # Check sanitization
#         if (timezone.now() - theater.last_sanitized).days > 1:
#             return False
            
#         # Check equipment status
#         if 'maintenance' in theater.equipment_status.lower():
#             return False
            
#         # Check existing bookings
#         return not Surgery.objects.filter(
#             operation_theater=theater,
#             scheduled_date__range=(
#                 surgery_date - timedelta(hours=2),
#                 surgery_date + timedelta(hours=2)
#             ),
#             status__in=['scheduled', 'in_progress']
#         ).exists()

#     def _validate_surgical_team(self, data):
#         surgery_date = data['scheduled_date']
#         primary_surgeon = data['primary_surgeon']
        
#         # Check primary surgeon availability
#         primary_surgeon_available = not Surgery.objects.filter(
#             primary_surgeon=primary_surgeon,
#             scheduled_date__range=(
#                 surgery_date - timedelta(hours=2),
#                 surgery_date + timedelta(hours=2)
#             ),
#             status__in=['scheduled', 'in_progress']
#         ).exists()
        
#         if not primary_surgeon_available:
#             return False
            
#         # Check assisting surgeons availability
#         for surgeon in data['assisting_surgeons']:
#             if Surgery.objects.filter(
#                 primary_surgeon=surgeon,
#                 scheduled_date__range=(
#                     surgery_date - timedelta(hours=2),
#                     surgery_date + timedelta(hours=2)
#                 ),
#                 status__in=['scheduled', 'in_progress']
#             ).exists():
#                 return False
                
#         return True

#     def _validate_patient_readiness(self, data):
#         patient = data['patient']
        
#         # Check if patient has other surgeries scheduled
#         has_other_surgeries = Surgery.objects.filter(
#             patient=patient,
#             scheduled_date__range=(
#                 data['scheduled_date'] - timedelta(days=7),
#                 data['scheduled_date'] + timedelta(days=7)
#             ),
#             status='scheduled'
#         ).exists()
        
#         if has_other_surgeries:
#             return False