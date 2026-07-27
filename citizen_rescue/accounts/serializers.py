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
            'phone_number', 'alternate_phone', 'address', 'profile_picture',
            'is_verified', 'created_at', 'updated_at',
            'resident_profile', 'guardian_profile', 'volunteer_profile',
            'security_profile'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']
