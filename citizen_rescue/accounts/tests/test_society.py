from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import Society, Block, Flat, ResidentProfile

User = get_user_model()

class SocietyManagementTests(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="Password123!",
            phone_number="9999999999",
            age=35
        )
        self.resident_user = User.objects.create_user(
            username="resident_user",
            email="resident@example.com",
            password="Password123!",
            phone_number="1234567890",
            age=30,
            role="RESIDENT"
        )
        
        # Create standard instances
        self.society = Society.objects.create(
            name="Green Valley",
            address="123 Main Road",
            registration_number="REG-12345",
            contact_info="greenvalley@example.com"
        )
        self.block = Block.objects.create(
            society=self.society,
            name="Block A"
        )
        self.flat = Flat.objects.create(
            block=self.block,
            flat_number="101"
        )
        
        # Endpoints
        self.society_list_url = reverse('society-list')
        self.block_list_url = reverse('block-list')
        self.flat_list_url = reverse('flat-list')

    def test_read_societies_authenticated(self):
        self.client.force_authenticate(user=self.resident_user)
        response = self.client.get(self.society_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Green Valley")
        self.assertEqual(response.data[0]['registration_number'], "REG-12345")
        self.assertEqual(response.data[0]['contact_info'], "greenvalley@example.com")

    def test_create_society_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Blue Sky Apartments",
            "address": "456 High St",
            "registration_number": "REG-67890",
            "contact_info": "bluesky@example.com"
        }
        response = self.client.post(self.society_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Society.objects.filter(name="Blue Sky Apartments").exists())

    def test_create_society_resident_forbidden(self):
        self.client.force_authenticate(user=self.resident_user)
        data = {
            "name": "Blue Sky Apartments",
            "address": "456 High St"
        }
        response = self.client.post(self.society_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_flat_mapping_via_profile(self):
        # Register a new resident with a flat assignment
        register_url = reverse('auth_register')
        data = {
            "username": "new_resident",
            "email": "new_resident@example.com",
            "password": "Password123!",
            "role": "RESIDENT",
            "phone_number": "9876543210",
            "age": 28,
            "flat": self.flat.id
        }
        response = self.client.post(register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the user has a profile mapped to the correct flat
        user = User.objects.get(username="new_resident")
        self.assertEqual(user.role, User.Role.RESIDENT)
        self.assertEqual(user.resident_profile.flat, self.flat)
