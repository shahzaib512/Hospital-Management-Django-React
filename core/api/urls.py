from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.user_view import UserViewSet, ProfileViewSet
from .views.patient_view import BedViewSet, PatientViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'beds', BedViewSet, basename='bed')
router.register(r'patients', PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
]
