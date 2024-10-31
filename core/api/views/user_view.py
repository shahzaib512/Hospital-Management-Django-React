# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from api.serializers.user_serializer import UserSerializer, ProfileSerializer, LoginSerializer
from api.models.user_model import Profile
from api.permission.permissions import IsAdminUser, IsDoctorUser
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_permissions(self):
        """
        Define permission based on action
        """
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        Filter queryset based on user role and optimize queries
        """
        user = self.request.user
        queryset = User.objects.select_related('profile', 'branch')
        
        if user.is_authenticated and user.is_admin:
            return queryset.all()
        return queryset.filter(id=user.id)
    
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new user with improved error handling
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            
            # Update last login IP
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                user.last_login_ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
            else:
                user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save(update_fields=['last_login_ip'])

            return Response({
                'status': 'success',
                'message': 'User created successfully',
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating the user',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user details
        """
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = self.get_serializer(request.user)
        return Response({
            'status': 'success',
            'user': serializer.data
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password with improved validation
        """
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'status': 'error',
                'message': 'Both old and new passwords are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.check_password(old_password):
            return Response({
                'status': 'error',
                'message': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Validate new password
            validate_password(new_password, request.user)
            
            # Set new password
            request.user.set_password(new_password)
            request.user.save()
            
            # Invalidate all existing tokens
            RefreshToken.for_user(request.user)
            
            return Response({
                'status': 'success',
                'message': 'Password updated successfully'
            })
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        User login with proper authentication
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Update last login IP
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            user.last_login_ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
        else:
            user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip'])
        
        return Response({
            'status': 'success',
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        User logout with improved error handling
        """
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({
                    'status': 'error',
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'status': 'success',
                'message': 'Successfully logged out'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset and optimize queries
        """
        return Profile.objects.filter(user=self.request.user).select_related('user')

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create profile with proper error handling
        """
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise ValidationError(f"Error creating profile: {str(e)}")

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Update profile with proper error handling
        """
        try:
            serializer.save()
        except Exception as e:
            raise ValidationError(f"Error updating profile: {str(e)}")