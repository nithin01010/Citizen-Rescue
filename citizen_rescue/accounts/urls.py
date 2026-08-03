from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    RegisterView, UserProfileView,
    UserViewSet, ResidentProfileViewSet, GuardianProfileViewSet,
    VolunteerProfileViewSet, SecurityProfileViewSet, EmergencyContactViewSet,
    SocietyViewSet, BlockViewSet, FlatViewSet, SOSAlertViewSet,
    NotificationLogViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'residents', ResidentProfileViewSet)
router.register(r'guardians', GuardianProfileViewSet)
router.register(r'volunteers', VolunteerProfileViewSet)
router.register(r'security', SecurityProfileViewSet)
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergencycontact')
router.register(r'societies', SocietyViewSet, basename='society')
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'flats', FlatViewSet, basename='flat')
router.register(r'alerts', SOSAlertViewSet, basename='sosalert')
router.register(r'notification-logs', NotificationLogViewSet, basename='notificationlog')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
