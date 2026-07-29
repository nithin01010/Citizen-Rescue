from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import EmergencyContact
from .test_data import (
    RESIDENT_USER_DATA,
    GUARDIAN_USER_DATA,
    OTHER_USER_DATA,
    ADMIN_USER_DATA,
    EMERGENCY_CONTACT_POST_DATA
)

User = get_user_model()

class EmergencyContactTests(APITestCase):
    def setUp(self):
        self.resident = User.objects.create_user(
            username=RESIDENT_USER_DATA["username"],
            email=RESIDENT_USER_DATA["email"],
            password=RESIDENT_USER_DATA["password"],
            phone_number=RESIDENT_USER_DATA["phone_number"],
            age=RESIDENT_USER_DATA["age"],
            role=RESIDENT_USER_DATA["role"]
        )
        self.guardian = User.objects.create_user(
            username=GUARDIAN_USER_DATA["username"],
            email=GUARDIAN_USER_DATA["email"],
            password=GUARDIAN_USER_DATA["password"],
            phone_number=GUARDIAN_USER_DATA["phone_number"],
            age=GUARDIAN_USER_DATA["age"],
            role=GUARDIAN_USER_DATA["role"],
            first_name=GUARDIAN_USER_DATA.get("first_name", ""),
            last_name=GUARDIAN_USER_DATA.get("last_name", "")
        )
        self.other_user = User.objects.create_user(
            username=OTHER_USER_DATA["username"],
            email=OTHER_USER_DATA["email"],
            password=OTHER_USER_DATA["password"],
            phone_number=OTHER_USER_DATA["phone_number"],
            age=OTHER_USER_DATA["age"],
            role=OTHER_USER_DATA["role"]
        )
        self.admin = User.objects.create_superuser(
            username=ADMIN_USER_DATA["username"],
            email=ADMIN_USER_DATA["email"],
            password=ADMIN_USER_DATA["password"],
            phone_number=ADMIN_USER_DATA["phone_number"],
            age=ADMIN_USER_DATA["age"]
        )
        self.url = reverse('emergencycontact-list')

    def test_create_emergency_contact_auto_resident(self):
        self.client.force_authenticate(user=self.resident)
        data = EMERGENCY_CONTACT_POST_DATA.copy()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['resident'], self.resident.id)

    def test_create_emergency_contact_auto_populate_guardian(self):
        self.client.force_authenticate(user=self.resident)
        data = {
            "guardian": self.guardian.id,
            "relationship": "Father",
            "priority": "SECONDARY"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], f"{self.guardian.first_name} {self.guardian.last_name}".strip())
        self.assertEqual(response.data['phone_number'], self.guardian.phone_number)

    def test_visibility_isolation(self):
        EmergencyContact.objects.create(
            resident=self.resident,
            name="John Doe",
            phone_number="9998887777",
            relationship="Friend",
            priority="PRIMARY"
        )
        self.client.force_authenticate(user=self.resident)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

    def test_duplicate_priority_constraint(self):
        self.client.force_authenticate(user=self.resident)
        EmergencyContact.objects.create(
            resident=self.resident,
            name="John Doe",
            phone_number="9998887777",
            relationship="Friend",
            priority="PRIMARY"
        )
        data = {
            "name": "Jane Doe",
            "phone_number": "1112223333",
            "relationship": "Sister",
            "priority": "PRIMARY"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_emergency_contact_by_guardian(self):
        contact = EmergencyContact.objects.create(
            resident=self.resident,
            guardian=self.guardian,
            name="Guardian One",
            phone_number="0987654321",
            relationship="Father",
            priority="PRIMARY"
        )
        verify_url = reverse('emergencycontact-verify', kwargs={'pk': contact.pk})
        
        self.client.force_authenticate(user=self.resident)
        response = self.client.post(verify_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.guardian)
        response = self.client.post(verify_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertTrue(contact.is_verified)
