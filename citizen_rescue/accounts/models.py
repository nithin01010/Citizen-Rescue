from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        RESIDENT = 'RESIDENT'
        GUARDIAN = 'GUARDIAN'
        VOLUNTEER = 'VOLUNTEER'
        SECURITY = 'SECURITY'
        ADMIN = 'ADMIN'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
    )
    phone_number = models.CharField(max_length=15, unique=True, null=False)
    age = models.IntegerField()
    alternate_phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    # profile_picture = models.ImageField(
    # upload_to='profiles/', null=True, blank=True
    # )
    is_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email', 'phone_number', 'age']


class Society(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class Block(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['society', 'name'],
                name='unique_society_block'
            )
        ]

    def __str__(self):
        return f"{self.society.name} - {self.name}"


class Flat(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='flats')
    flat_number = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['block', 'flat_number'],
                name='unique_block_flat'
            )
        ]

    def __str__(self):
        return f"{self.block.name} - {self.flat_number}"


class ResidentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='resident_profile',
        limit_choices_to={'role': User.Role.RESIDENT}
    )
    flat = models.ForeignKey(
        Flat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='residents'
    )
    emergency_notes = models.TextField(
        blank=True,
        null=True,
    )
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    is_senior_citizen = models.BooleanField(default=False)

    def __str__(self):
        return f"Resident Profile: {self.user.username}"


class GuardianProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='guardian_profile',
        limit_choices_to={'role': User.Role.GUARDIAN}
    )
    occupation = models.CharField(max_length=100, blank=True, null=True)
    relation_notes = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Guardian Profile: {self.user.username}"


class VolunteerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
        limit_choices_to={'role': User.Role.VOLUNTEER}
    )
    skills = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    is_available = models.BooleanField(default=True,)
    id_proof_type = models.CharField(max_length=50, blank=True, null=True)
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Volunteer Profile: {self.user.username}"


class SecurityProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='security_profile',
        limit_choices_to={'role': User.Role.SECURITY}
    )
    badge_number = models.CharField(max_length=50, unique=True)
    shift_timing = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    assigned_gate = models.CharField(max_length=50, blank=True, null=True)
    on_duty = models.BooleanField(default=True)

    def __str__(self):
        return f"""Security Personnel:
        {self.user.username} (Badge: {self.badge_number})"""


class EmergencyContact(models.Model):
    class Priority(models.TextChoices):
        PRIMARY = 'PRIMARY', 'Primary Guardian'
        SECONDARY = 'SECONDARY', 'Secondary Guardian'
        TERTIARY = 'TERTIARY', 'General Contact'

    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        limit_choices_to={'role': User.Role.RESIDENT}
    )
    guardian = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guardian_contacts',
        limit_choices_to={'role': User.Role.GUARDIAN}
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.PRIMARY
    )
    is_verified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['resident', 'priority'],
                name='unique_resident_contact_priority'
            )
        ]

    def __str__(self):
        return f"{self.resident.username}'s {self.priority} Contact: {self.name}"
