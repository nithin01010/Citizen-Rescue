from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    User,
    ResidentProfile,
    GuardianProfile,
    VolunteerProfile,
    SecurityProfile,
)
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ResidentProfileSerializer,
    GuardianProfileSerializer,
    VolunteerProfileSerializer,
    SecurityProfileSerializer,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.pop('refresh', None)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        return Response({
            "message": "User registered successfully",
            "user": user_data
        }, status=status.HTTP_201_CREATED)


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
