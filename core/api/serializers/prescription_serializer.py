from rest_framework import serializers
from api.models.prescription_model import Prescription, Medication
from api.serializers.staff_serializer import DoctorSerializer
from api.serializers.patient_serializer import PatientSerializer
from django.core.cache import cache

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'dosage', 'frequency', 'duration', 'instructions']

class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'doctor', 'prescription_date',
            'diagnosis', 'medications', 'notes', 'status',
            'doctor_details', 'patient_details'
        ]

    def create(self, validated_data):
        medications_data = validated_data.pop('medications', [])
        prescription = Prescription.objects.create(**validated_data)

        for medication_data in medications_data:
            Medication.objects.create(prescription=prescription, **medication_data)

        return prescription

    def update(self, instance, validated_data):
        medications_data = validated_data.pop('medications', [])
        
        # Update prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update medications
        instance.medications.all().delete()
        for medication_data in medications_data:
            Medication.objects.create(prescription=instance, **medication_data)

        return instance

    def validate(self, data):
        # Validate that the doctor is assigned to the patient
        if 'doctor' in data and 'patient' in data:
            doctor = data['doctor']
            patient = data['patient']
            if not patient.doctors.filter(id=doctor.id).exists():
                raise serializers.ValidationError(
                    "This doctor is not assigned to the patient"
                )
        return data