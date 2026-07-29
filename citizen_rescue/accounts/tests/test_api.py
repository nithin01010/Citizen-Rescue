from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import (
    ResidentProfile, GuardianProfile, VolunteerProfile, SecurityProfile, EmergencyContact
)

User = get_user_model()

class RegistrationTests(APITestCase):
    def test_register_resident(self):
        url = reverse('auth_register')
        data = {
            "username": "resident1",
            "email": "resident1@example.com",
            "password": "Password123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "RESIDENT",
            "phone_number": "1234567890",
            "age": 30,
            "blood_group": "O+",
            "medical_conditions": "None",
            "is_senior_citizen": False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="resident1").exists())
        user = User.objects.get(username="resident1")
        self.assertEqual(user.role, User.Role.RESIDENT)
        self.assertTrue(ResidentProfile.objects.filter(user=user).exists())
        profile = user.resident_profile
        self.assertEqual(profile.blood_group, "O+")

    def test_register_guardian(self):
        url = reverse('auth_register')
        data = {
            "username": "guardian1",
            "email": "guardian1@example.com",
            "password": "Password123!",
            "first_name": "Jane",
            "last_name": "Doe",
            "role": "GUARDIAN",
            "phone_number": "0987654321",
            "age": 45,
            "occupation": "Doctor",
            "relation_notes": "Neighbor"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="guardian1")
        self.assertEqual(user.role, User.Role.GUARDIAN)
        self.assertTrue(GuardianProfile.objects.filter(user=user).exists())

    def test_register_volunteer(self):
        url = reverse('auth_register')
        data = {
            "username": "volunteer1",
            "email": "volunteer1@example.com",
            "password": "Password123!",
            "first_name": "Jack",
            "last_name": "Smith",
            "role": "VOLUNTEER",
            "phone_number": "1112223333",
            "age": 25,
            "skills": "First Aid",
            "id_proof_type": "Aadhaar",
            "id_proof_number": "123456789012"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="volunteer1")
        self.assertEqual(user.role, User.Role.VOLUNTEER)
        self.assertTrue(VolunteerProfile.objects.filter(user=user).exists())

    def test_register_security(self):
        url = reverse('auth_register')
        data = {
            "username": "security1",
            "email": "security1@example.com",
            "password": "Password123!",
            "first_name": "Officer",
            "last_name": "Bob",
            "role": "SECURITY",
            "phone_number": "4445556666",
            "age": 40,
            "badge_number": "SEC-001",
            "assigned_gate": "Gate 1",
            "shift_timing": "Day"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="security1")
        self.assertEqual(user.role, User.Role.SECURITY)
        self.assertTrue(SecurityProfile.objects.filter(user=user).exists())


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!",
            phone_number="1234567890",
            age=30
        )
        self.login_url = reverse('token_obtain')

    def test_login_success(self):
        data = {
            "username": "testuser",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        # Custom serializer should exclude refresh token
        self.assertNotIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!",
            phone_number="1234567890",
            age=30,
            address="123 Street"
        )
        self.profile_url = reverse('user_profile')

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], "testuser")
        self.assertEqual(response.data['address'], "123 Street")

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "address": "456 Avenue",
            "alternate_phone": "9876543210"
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.address, "456 Avenue")
        self.assertEqual(self.user.alternate_phone, "9876543210")


class EmergencyContactTests(APITestCase):
    def setUp(self):
        self.resident = User.objects.create_user(
            username="resident1",
            email="resident1@example.com",
            password="Password123!",
            phone_number="1234567890",
            age=30,
            role=User.Role.RESIDENT
        )
        self.guardian = User.objects.create_user(
            username="guardian1",
            email="guardian1@example.com",
            password="Password123!",
            phone_number="0987654321",
            age=40,
            role=User.Role.GUARDIAN,
            first_name="Guardian",
            last_name="One"
        )
        self.other_user = User.objects.create_user(
            username="other1",
            email="other1@example.com",
            password="Password123!",
            phone_number="5555555555",
            age=25,
            role=User.Role.RESIDENT
        )
        self.admin = User.objects.create_superuser(
            username="admin1",
            email="admin1@example.com",
            password="Password123!",
            phone_number="9999999999",
            age=35
        )
        self.url = reverse('emergencycontact-list')

    def test_create_emergency_contact_auto_resident(self):
        self.client.force_authenticate(user=self.resident)
        data = {
            "name": "Jane Doe",
            "phone_number": "1112223333",
            "relationship": "Sister",
            "priority": "PRIMARY"
        }
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
        self.assertEqual(response.data['name'], "Guardian One")
        self.assertEqual(response.data['phone_number'], "0987654321")

    def test_visibility_isolation(self):
        # Create a contact for resident1
        EmergencyContact.objects.create(
            resident=self.resident,
            name="John Doe",
            phone_number="9998887777",
            relationship="Friend",
            priority="PRIMARY"
        )

        # resident1 should see it
        self.client.force_authenticate(user=self.resident)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 1)

        # other_user should not see it
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)

        # admin should see it
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
