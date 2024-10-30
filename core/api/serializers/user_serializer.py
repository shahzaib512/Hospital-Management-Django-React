from api.models import User, Branch
from api.models.user_model import Profile
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    branch_details = BranchSerializer(source='branch', required=False)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'confirm_password',
                  'full_name', 'phone', 'role', 'branch', 'branch_details',
                  'profile', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['is_active', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        profile_data = validated_data.pop('profile', None)
        
        user = User.objects.create_user(**validated_data)
        
        if profile_data:
            Profile.objects.filter(user=user).update(**profile_data)
        
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        profile_data = validated_data.pop('profile', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            Profile.objects.filter(user=instance).update(**profile_data)

        return instance

