from rest_framework import serializers
from .models import (
    User,
    ResidentProfile,
    GuardianProfile,
    VolunteerProfile,
    SecurityProfile
)


class ResidentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = '__all__'


class GuardianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianProfile
        fields = '__all__'


class VolunteerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = '__all__'


class SecurityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    resident_profile = ResidentProfileSerializer(read_only=True)
    guardian_profile = GuardianProfileSerializer(read_only=True)
    volunteer_profile = VolunteerProfileSerializer(read_only=True)
    security_profile = SecurityProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'age', 'alternate_phone', 'address',
            'is_verified', 'resident_profile', 'guardian_profile',
            'volunteer_profile', 'security_profile'
        ]
        read_only_fields = ['id', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone_number', 'age', 'alternate_phone', 'address'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.RESIDENT)
        user = User.objects.create_user(password=password, **validated_data)

        if role == User.Role.RESIDENT:
            ResidentProfile.objects.get_or_create(user=user)
        elif role == User.Role.GUARDIAN:
            GuardianProfile.objects.get_or_create(user=user)
        elif role == User.Role.VOLUNTEER:
            VolunteerProfile.objects.get_or_create(user=user)
        elif role == User.Role.SECURITY:
            SecurityProfile.objects.get_or_create(user=user)

        return user
