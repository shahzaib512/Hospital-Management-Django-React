from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.user_view import UserViewSet, ProfileViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
