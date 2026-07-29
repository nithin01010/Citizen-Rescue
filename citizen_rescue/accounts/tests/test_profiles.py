from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import (
    ResidentProfile, GuardianProfile, VolunteerProfile, SecurityProfile
)
from .test_data import (
    RESIDENT_USER_DATA,
    GUARDIAN_USER_DATA,
    OTHER_USER_DATA
)

User = get_user_model()

class ProfileTests(APITestCase):
    def setUp(self):
        self.resident_user = User.objects.create_user(
            username=RESIDENT_USER_DATA["username"],
            email=RESIDENT_USER_DATA["email"],
            password=RESIDENT_USER_DATA["password"],
            phone_number=RESIDENT_USER_DATA["phone_number"],
            age=RESIDENT_USER_DATA["age"],
            role=RESIDENT_USER_DATA["role"],
            address=RESIDENT_USER_DATA["address"]
        )
        self.resident_profile = ResidentProfile.objects.create(
            user=self.resident_user,
            blood_group="O+"
        )

        self.guardian_user = User.objects.create_user(
            username=GUARDIAN_USER_DATA["username"],
            email=GUARDIAN_USER_DATA["email"],
            password=GUARDIAN_USER_DATA["password"],
            phone_number=GUARDIAN_USER_DATA["phone_number"],
            age=GUARDIAN_USER_DATA["age"],
            role=GUARDIAN_USER_DATA["role"]
        )
        self.guardian_profile = GuardianProfile.objects.create(
            user=self.guardian_user,
            occupation="Engineer"
        )

        self.other_user = User.objects.create_user(
            username=OTHER_USER_DATA["username"],
            email=OTHER_USER_DATA["email"],
            password=OTHER_USER_DATA["password"],
            phone_number=OTHER_USER_DATA["phone_number"],
            age=OTHER_USER_DATA["age"],
            role=OTHER_USER_DATA["role"]
        )
        self.me_url = reverse('user_profile')

    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me_authenticated(self):
        self.client.force_authenticate(user=self.resident_user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], RESIDENT_USER_DATA["username"])

    def test_patch_me(self):
        self.client.force_authenticate(user=self.resident_user)
        data = {"address": "456 Avenue"}
        response = self.client.patch(self.me_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resident_user.refresh_from_db()
        self.assertEqual(self.resident_user.address, "456 Avenue")

    def test_patch_resident_profile_owner(self):
        self.client.force_authenticate(user=self.resident_user)
        url = reverse('residentprofile-detail', kwargs={'pk': self.resident_profile.pk})
        data = {"blood_group": "AB-"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.resident_profile.refresh_from_db()
        self.assertEqual(self.resident_profile.blood_group, "AB-")

    def test_patch_resident_profile_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse('residentprofile-detail', kwargs={'pk': self.resident_profile.pk})
        data = {"blood_group": "A-"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_guardian_profile_owner(self):
        self.client.force_authenticate(user=self.guardian_user)
        url = reverse('guardianprofile-detail', kwargs={'pk': self.guardian_profile.pk})
        data = {"occupation": "Doctor"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.guardian_profile.refresh_from_db()
        self.assertEqual(self.guardian_profile.occupation, "Doctor")

    def test_patch_guardian_profile_forbidden(self):
        self.client.force_authenticate(user=self.resident_user)
        url = reverse('guardianprofile-detail', kwargs={'pk': self.guardian_profile.pk})
        data = {"occupation": "Spy"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
