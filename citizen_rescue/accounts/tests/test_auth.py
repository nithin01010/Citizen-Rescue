from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .test_data import TEST_USER_CREDENTIALS

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=TEST_USER_CREDENTIALS["username"],
            email=TEST_USER_CREDENTIALS["email"],
            password=TEST_USER_CREDENTIALS["password"],
            phone_number=TEST_USER_CREDENTIALS["phone_number"],
            age=TEST_USER_CREDENTIALS["age"]
        )
        self.login_url = reverse('token_obtain')

    def test_login_success(self):
        data = {
            "username": TEST_USER_CREDENTIALS["username"],
            "password": TEST_USER_CREDENTIALS["password"]
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {
            "username": TEST_USER_CREDENTIALS["username"],
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
