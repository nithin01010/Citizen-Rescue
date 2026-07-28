from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    RegisterView, UserProfileView,
    UserViewSet, ResidentProfileViewSet, GuardianProfileViewSet,
    VolunteerProfileViewSet, SecurityProfileViewSet, EmergencyContactViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'residents', ResidentProfileViewSet)
router.register(r'guardians', GuardianProfileViewSet)
router.register(r'volunteers', VolunteerProfileViewSet)
router.register(r'security', SecurityProfileViewSet)
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergencycontact')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
