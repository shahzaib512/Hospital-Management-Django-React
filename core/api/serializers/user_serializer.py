
from api.models.user_model import Profile, User, Branch
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction


User = get_user_model()

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']
        
    def validate(self, attrs):
        # Get the request context
        request = self.context.get('request')
        
        # Get the user role from either the request data (for registration) 
        # or the authenticated user (for profile updates)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_role = request.user.role
        else:
            # For registration, get role from parent serializer's context
            user_role = self.context.get('user_role')
            
        if user_role:
            if user_role == 'doctor':
                required_fields = ['qualification', 'specialization', 'license_number']
                for field in required_fields:
                    if not attrs.get(field):
                        raise serializers.ValidationError(f"{field} is required for doctors")
            elif user_role == 'patient':
                required_fields = ['date_of_birth', 'blood_group']
                for field in required_fields:
                    if not attrs.get(field):
                        raise serializers.ValidationError(f"{field} is required for patients")
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    branch_details = BranchSerializer(source='branch', read_only=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password',
            'full_name', 'phone', 'role', 'branch', 'branch_details',
            'profile', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['is_active', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'role': {'required': True}
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate email uniqueness
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email address already exists."})
            
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            validated_data.pop('confirm_password', None)
            profile_data = validated_data.pop('profile', None)
            branch_data = validated_data.pop('branch', None)
            
            # Create user first
            user = User.objects.create_user(**validated_data)
            
            # Handle branch assignment
            if branch_data:
                branch = Branch.objects.filter(id=branch_data).first()
                if not branch:
                    raise serializers.ValidationError({"branch": "Branch does not exist."})
                user.branch = branch
                user.save()
            
            # Handle profile creation
            if profile_data:
                # Pass the user role to profile serializer for validation
                profile_serializer = ProfileSerializer(
                    data=profile_data,
                    context={'user_role': validated_data.get('role')}
                )
                if profile_serializer.is_valid(raise_exception=True):
                    Profile.objects.filter(user=user).update(**profile_data)
            
            return user

    def update(self, instance, validated_data):
        with transaction.atomic():
            validated_data.pop('password', None)
            validated_data.pop('confirm_password', None)
            profile_data = validated_data.pop('profile', None)
            branch_data = validated_data.pop('branch', None)
            
            # Update user fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Handle branch update
            if branch_data:
                branch = Branch.objects.filter(id=branch_data).first()
                if not branch:
                    raise serializers.ValidationError({"branch": "Branch does not exist."})
                instance.branch = branch
                instance.save()
            
            # Handle profile update
            if profile_data:
                profile_serializer = ProfileSerializer(
                    instance.profile,
                    data=profile_data,
                    context={'request': self.context.get('request')}
                )
                if profile_serializer.is_valid(raise_exception=True):
                    Profile.objects.filter(user=instance).update(**profile_data)
            
            return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError('Must include "email" and "password".')