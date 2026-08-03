from django.db import models
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsOwnerOrAdminOrReadOnly
from .models import (
    User, ResidentProfile, GuardianProfile, VolunteerProfile, SecurityProfile,
    EmergencyContact, Society, Block, Flat, SOSAlert, NotificationLog
)
from .serializers import (
    UserSerializer, RegisterSerializer, ResidentProfileSerializer,
    GuardianProfileSerializer, VolunteerProfileSerializer, SecurityProfileSerializer,
    EmergencyContactSerializer, SocietySerializer, BlockSerializer,
    FlatSerializer, SOSAlertSerializer, NotificationLogSerializer
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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class ResidentProfileViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class GuardianProfileViewSet(viewsets.ModelViewSet):
    queryset = GuardianProfile.objects.all()
    serializer_class = GuardianProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class VolunteerProfileViewSet(viewsets.ModelViewSet):
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class SecurityProfileViewSet(viewsets.ModelViewSet):
    queryset = SecurityProfile.objects.all()
    serializer_class = SecurityProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class EmergencyContactViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMIN:
            return EmergencyContact.objects.all()
        return EmergencyContact.objects.filter(models.Q(resident=user) | models.Q(guardian=user))

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify(self, request, pk=None):
        contact = self.get_object()
        
        # Only the designated guardian can verify the contact
        if contact.guardian != request.user:
            return Response(
                {"detail": "Only the designated guardian can verify this contact."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        contact.is_verified = True
        contact.save()
        
        serializer = self.get_serializer(contact)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocietyViewSet(viewsets.ModelViewSet):
    queryset = Society.objects.all()
    serializer_class = SocietySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]


class SOSAlertViewSet(viewsets.ModelViewSet):
    serializer_class = SOSAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMIN:
            return SOSAlert.objects.all()
            
        if user.role == User.Role.RESIDENT:
            return SOSAlert.objects.filter(resident=user)
            
        if user.role == User.Role.GUARDIAN:
            return SOSAlert.objects.filter(
                resident__emergency_contacts__guardian=user
            ).distinct()
            
        if user.role in [User.Role.SECURITY, User.Role.VOLUNTEER]:
            return SOSAlert.objects.all()
            
        return SOSAlert.objects.none()

    def perform_create(self, serializer):
        alert = serializer.save(resident=self.request.user, status=SOSAlert.Status.OPEN)
        
        # 1. Notify Guardians
        guardian_contacts = EmergencyContact.objects.filter(
            resident=self.request.user,
            priority=EmergencyContact.Priority.PRIMARY
        )
        for contact in guardian_contacts:
            if contact.guardian:
                NotificationLog.objects.create(
                    alert=alert,
                    recipient=contact.guardian,
                    channel=NotificationLog.Channel.IN_APP,
                    status=NotificationLog.DeliveryStatus.SENT
                )
                
        # 2. Notify Security Personnel (on duty)
        security_profiles = SecurityProfile.objects.filter(on_duty=True)
        for profile in security_profiles:
            NotificationLog.objects.create(
                alert=alert,
                recipient=profile.user,
                channel=NotificationLog.Channel.IN_APP,
                status=NotificationLog.DeliveryStatus.SENT
            )
            
        # 3. Notify Volunteers (available)
        volunteer_profiles = VolunteerProfile.objects.filter(is_available=True)
        for profile in volunteer_profiles:
            NotificationLog.objects.create(
                alert=alert,
                recipient=profile.user,
                channel=NotificationLog.Channel.IN_APP,
                status=NotificationLog.DeliveryStatus.SENT
            )


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMIN:
            return NotificationLog.objects.all()
        return NotificationLog.objects.filter(
            models.Q(recipient=user) | models.Q(alert__resident=user)
        ).distinct()

