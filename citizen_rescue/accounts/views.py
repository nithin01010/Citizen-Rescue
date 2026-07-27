from rest_framework import viewsets, permissions
from .models import (
    User,
    ResidentProfile,
    GuardianProfile,
    VolunteerProfile,
    SecurityProfile,
)
from .serializers import (
    UserSerializer,
    ResidentProfileSerializer,
    GuardianProfileSerializer,
    VolunteerProfileSerializer,
    SecurityProfileSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ResidentProfileViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = GuardianProfile.objects.all()
    serializer_class = GuardianProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class VolunteerProfileViewSet(viewsets.ModelViewSet):
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SecurityProfileViewSet(viewsets.ModelViewSet):
    queryset = SecurityProfile.objects.all()
    serializer_class = SecurityProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
