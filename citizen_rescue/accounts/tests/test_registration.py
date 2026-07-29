from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import (
    ResidentProfile, GuardianProfile, VolunteerProfile, SecurityProfile, Block, Flat, Society
)
from .test_data import (
    RESIDENT_REGISTRATION_DATA,
    RESIDENT_WITH_FLAT_REGISTRATION_DATA,
    GUARDIAN_REGISTRATION_DATA,
    VOLUNTEER_REGISTRATION_DATA,
    SECURITY_REGISTRATION_DATA
)

User = get_user_model()

class RegistrationTests(APITestCase):
    def test_register_resident(self):
        url = reverse('auth_register')
        data = RESIDENT_REGISTRATION_DATA.copy()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=RESIDENT_REGISTRATION_DATA['username']).exists())
        user = User.objects.get(username=RESIDENT_REGISTRATION_DATA['username'])
        self.assertEqual(user.role, User.Role.RESIDENT)
        self.assertTrue(ResidentProfile.objects.filter(user=user).exists())
        profile = user.resident_profile
        self.assertEqual(profile.blood_group, RESIDENT_REGISTRATION_DATA['blood_group'])

    def test_register_resident_with_flat(self):
        society = Society.objects.create(name="Apex Society", address="123 Road")
        block = Block.objects.create(name="Block C", society=society)
        flat = Flat.objects.create(block=block, flat_number="301")
        
        url = reverse('auth_register')
        data = RESIDENT_WITH_FLAT_REGISTRATION_DATA.copy()
        data["flat"] = flat.id
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=RESIDENT_WITH_FLAT_REGISTRATION_DATA['username'])
        self.assertEqual(user.resident_profile.flat, flat)

    def test_register_guardian(self):
        url = reverse('auth_register')
        data = GUARDIAN_REGISTRATION_DATA.copy()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=GUARDIAN_REGISTRATION_DATA['username'])
        self.assertEqual(user.role, User.Role.GUARDIAN)
        self.assertTrue(GuardianProfile.objects.filter(user=user).exists())

    def test_register_volunteer(self):
        url = reverse('auth_register')
        data = VOLUNTEER_REGISTRATION_DATA.copy()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=VOLUNTEER_REGISTRATION_DATA['username'])
        self.assertEqual(user.role, User.Role.VOLUNTEER)
        self.assertTrue(VolunteerProfile.objects.filter(user=user).exists())

    def test_register_security(self):
        url = reverse('auth_register')
        data = SECURITY_REGISTRATION_DATA.copy()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=SECURITY_REGISTRATION_DATA['username'])
        self.assertEqual(user.role, User.Role.SECURITY)
        self.assertTrue(SecurityProfile.objects.filter(user=user).exists())
