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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    blood_group = serializers.CharField(required=False, write_only=True)
    emergency_notes = serializers.CharField(required=False, write_only=True)
    medical_conditions = serializers.CharField(required=False, write_only=True)
    is_senior_citizen = serializers.BooleanField(required=False,
                                                 write_only=True)

    occupation = serializers.CharField(required=False, write_only=True)
    relation_notes = serializers.CharField(required=False, write_only=True)

    skills = serializers.CharField(required=False, write_only=True)
    id_proof_type = serializers.CharField(required=False, write_only=True)
    id_proof_number = serializers.CharField(required=False, write_only=True)

    badge_number = serializers.CharField(required=False, write_only=True)
    assigned_gate = serializers.CharField(required=False, write_only=True)
    shift_timing = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone_number', 'age', 'alternate_phone', 'address',
            'blood_group', 'emergency_notes', 'medical_conditions',
            'is_senior_citizen',
            'occupation', 'relation_notes',
            'skills', 'id_proof_type', 'id_proof_number',
            'badge_number', 'assigned_gate', 'shift_timing'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.RESIDENT)

        blood_group = validated_data.pop('blood_group')
        emergency_notes = validated_data.pop('emergency_notes')
        medical_conditions = validated_data.pop('medical_conditions')
        is_senior_citizen = validated_data.pop('is_senior_citizen')

        occupation = validated_data.pop('occupation')
        relation_notes = validated_data.pop('relation_notes')

        skills = validated_data.pop('skills')
        id_proof_type = validated_data.pop('id_proof_type')
        id_proof_number = validated_data.pop('id_proof_number')

        badge_number = validated_data.pop('badge_number')
        assigned_gate = validated_data.pop('assigned_gate')
        shift_timing = validated_data.pop('shift_timing')

        user = User.objects.create_user(password=password, **validated_data)

        if role == User.Role.RESIDENT:
            ResidentProfile.objects.create(
                user=user, blood_group=blood_group,
                emergency_notes=emergency_notes,
                medical_conditions=medical_conditions,
                is_senior_citizen=is_senior_citizen
            )
        elif role == User.Role.GUARDIAN:
            GuardianProfile.objects.create(
                user=user,
                occupation=occupation,
                relation_notes=relation_notes)
        elif role == User.Role.VOLUNTEER:
            VolunteerProfile.objects.create(
                user=user,
                skills=skills,
                id_proof_type=id_proof_type,
                id_proof_number=id_proof_number)
        elif role == User.Role.SECURITY:
            SecurityProfile.objects.create(
                user=user,
                badge_number=badge_number or f"SEC-{user.id}",
                assigned_gate=assigned_gate, shift_timing=shift_timing)

        return user
