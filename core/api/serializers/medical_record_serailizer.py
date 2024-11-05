from rest_framework import serializers
from api.models.medical_record_model import MedicalRecord, Attachment
from api.serializers.staff_serializer import DoctorSerializer
from api.serializers.patient_serializer import PatientSerializer
from api.serializers.prescription_serializer import PrescriptionSerializer

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_type', 'upload_date', 'description']

class MedicalRecordSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'doctor', 'record_date',
            'diagnosis', 'treatment_plan', 'notes',
            'attachments', 'doctor_details', 'patient_details',
            'prescriptions', 'vital_signs', 'allergies',
            'medical_history'
        ]

    def validate(self, data):
        # Validate record date is not in future
        if data.get('record_date') and data['record_date'] > timezone.now().date():
            raise serializers.ValidationError(
                {"record_date": "Record date cannot be in the future"}
            )
        return data

    def create(self, validated_data):
        attachments_data = self.context.get('attachments', [])
        medical_record = MedicalRecord.objects.create(**validated_data)

        # Handle attachments
        for attachment_data in attachments_data:
            Attachment.objects.create(medical_record=medical_record, **attachment_data)

        return medical_record

    def update(self, instance, validated_data):
        attachments_data = self.context.get('attachments', [])
        
        # Update medical record fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update attachments if provided
        if attachments_data:
            instance.attachments.all().delete()
            for attachment_data in attachments_data:
                Attachment.objects.create(medical_record=instance, **attachment_data)

        return instance