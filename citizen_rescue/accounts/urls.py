from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ResidentProfileViewSet, GuardianProfileViewSet,
    VolunteerProfileViewSet, SecurityProfileViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'residents', ResidentProfileViewSet)
router.register(r'guardians', GuardianProfileViewSet)
router.register(r'volunteers', VolunteerProfileViewSet)
router.register(r'security', SecurityProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
