from rest_framework import serializers
from .models import (
    User,
    ResidentProfile,
    GuardianProfile,
    VolunteerProfile,
    SecurityProfile,
    EmergencyContact,
    Flat,
)


class OptimizedModelSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        updated_fields = []
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
                updated_fields.append(attr)
        if updated_fields:
            instance.save(update_fields=updated_fields)
        return instance


class ResidentProfileSerializer(OptimizedModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = '__all__'


class GuardianProfileSerializer(OptimizedModelSerializer):
    class Meta:
        model = GuardianProfile
        fields = '__all__'


class VolunteerProfileSerializer(OptimizedModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = '__all__'


class SecurityProfileSerializer(OptimizedModelSerializer):
    class Meta:
        model = SecurityProfile
        fields = '__all__'


class EmergencyContactSerializer(OptimizedModelSerializer):
    resident_name = serializers.CharField(source='resident.username', read_only=True)
    guardian_name = serializers.CharField(source='guardian.username', read_only=True, default=None)

    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'resident', 'resident_name', 'guardian', 'guardian_name',
            'name', 'phone_number', 'relationship', 'priority', 'is_verified'
        ]
        read_only_fields = ['resident', 'is_verified']
        extra_kwargs = {
            'name': {'required': False},
            'phone_number': {'required': False}
        }

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user:
            resident = request.user
            priority = attrs.get('priority', 'PRIMARY')
            
            queryset = EmergencyContact.objects.filter(resident=resident, priority=priority)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    "priority": f"An emergency contact with priority '{priority}' already exists for this resident."
                })

        guardian = attrs.get('guardian')
        if guardian:
            if not attrs.get('name'):
                attrs['name'] = f"{guardian.first_name} {guardian.last_name}".strip() or guardian.username
            if not attrs.get('phone_number'):
                attrs['phone_number'] = guardian.phone_number
        else:
            if not attrs.get('name') or not attrs.get('phone_number'):
                raise serializers.ValidationError({
                    "name": "This field is required when no guardian is specified.",
                    "phone_number": "This field is required when no guardian is specified."
                })
        return attrs



class UserSerializer(OptimizedModelSerializer):
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
    flat = serializers.PrimaryKeyRelatedField(queryset=Flat.objects.all(), required=False, write_only=True)
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
            'flat',
            'blood_group', 'emergency_notes', 'medical_conditions',
            'is_senior_citizen',
            'occupation', 'relation_notes',
            'skills', 'id_proof_type', 'id_proof_number',
            'badge_number', 'assigned_gate', 'shift_timing'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.RESIDENT)

        flat = validated_data.pop('flat', None)
        blood_group = validated_data.pop('blood_group', None)
        emergency_notes = validated_data.pop('emergency_notes', None)
        medical_conditions = validated_data.pop('medical_conditions', None)
        is_senior_citizen = validated_data.pop('is_senior_citizen', False)

        occupation = validated_data.pop('occupation', None)
        relation_notes = validated_data.pop('relation_notes', None)

        skills = validated_data.pop('skills', None)
        id_proof_type = validated_data.pop('id_proof_type', None)
        id_proof_number = validated_data.pop('id_proof_number', None)

        badge_number = validated_data.pop('badge_number', None)
        assigned_gate = validated_data.pop('assigned_gate', None)
        shift_timing = validated_data.pop('shift_timing', None)

        user = User.objects.create_user(password=password, **validated_data)

        if role == User.Role.RESIDENT:
            ResidentProfile.objects.create(
                user=user,
                flat=flat,
                blood_group=blood_group,
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
