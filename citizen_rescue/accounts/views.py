from rest_framework import viewsets, generics, permissions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    User, ResidentProfile, GuardianProfile, VolunteerProfile, SecurityProfile
)
from .serializers import (
    UserSerializer, RegisterSerializer, ResidentProfileSerializer,
    GuardianProfileSerializer, VolunteerProfileSerializer, SecurityProfileSerializer
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.pop('refresh')
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResidentProfileViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = GuardianProfile.objects.all()
    serializer_class = GuardianProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class VolunteerProfileViewSet(viewsets.ModelViewSet):
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class SecurityProfileViewSet(viewsets.ModelViewSet):
    queryset = SecurityProfile.objects.all()
    serializer_class = SecurityProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
