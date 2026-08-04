from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import (
    SOSAlert, NotificationLog, EmergencyContact, SecurityProfile, VolunteerProfile
)

User = get_user_model()

class SOSAlertTests(APITestCase):
    def setUp(self):
        # Create a resident
        self.resident = User.objects.create_user(
            username="resident_user",
            email="resident@example.com",
            password="Password123!",
            phone_number="1234567890",
            age=30,
            role="RESIDENT"
        )
        
        # Create a guardian
        self.guardian = User.objects.create_user(
            username="guardian_user",
            email="guardian@example.com",
            password="Password123!",
            phone_number="0987654321",
            age=45,
            role="GUARDIAN"
        )
        
        # Set guardian as primary contact for resident
        self.primary_contact = EmergencyContact.objects.create(
            resident=self.resident,
            guardian=self.guardian,
            name="Guardian Name",
            phone_number="0987654321",
            relationship="Father",
            priority=EmergencyContact.Priority.PRIMARY,
            is_verified=True
        )

        # Create security personnel (on duty)
        self.security_user = User.objects.create_user(
            username="security_user",
            email="security@example.com",
            password="Password123!",
            phone_number="1112223333",
            age=40,
            role="SECURITY"
        )
        self.security_profile = SecurityProfile.objects.create(
            user=self.security_user,
            badge_number="SEC-123",
            on_duty=True
        )

        # Create a volunteer (available)
        self.volunteer_user = User.objects.create_user(
            username="volunteer_user",
            email="volunteer@example.com",
            password="Password123!",
            phone_number="4445556666",
            age=25,
            role="VOLUNTEER"
        )
        self.volunteer_profile = VolunteerProfile.objects.create(
            user=self.volunteer_user,
            is_available=True
        )

        # Endpoints
        self.alert_list_url = reverse('sosalert-list')

    def test_trigger_sos_alert(self):
        # Authenticate resident
        self.client.force_authenticate(user=self.resident)
        
        data = {
            "category": "MEDICAL",
            "message": "Chest pain, need help",
            "latitude": 12.971598,
            "longitude": 77.594562
        }
        
        response = self.client.post(self.alert_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['resident_name'], "resident_user")
        self.assertEqual(response.data['status'], "OPEN")
        
        # Verify SOSAlert object was saved to database
        alert_id = response.data['id']
        alert = SOSAlert.objects.get(id=alert_id)
        self.assertEqual(alert.resident, self.resident)
        self.assertEqual(alert.category, "MEDICAL")
        self.assertEqual(alert.message, "Chest pain, need help")
        
        # Verify routing logic: 8 notification logs should be created:
        # - Primary guardian (IN_APP, SMS, EMAIL, PUSH) -> 4 logs
        # - On-duty security (IN_APP, PUSH) -> 2 logs
        # - Available volunteer (IN_APP, PUSH) -> 2 logs
        logs = NotificationLog.objects.filter(alert=alert)
        self.assertEqual(logs.count(), 8)
        
        # Verify recipient counts
        guardian_logs = logs.filter(recipient=self.guardian)
        self.assertEqual(guardian_logs.count(), 4)
        self.assertEqual(
            set(guardian_logs.values_list('channel', flat=True)),
            {NotificationLog.Channel.IN_APP, NotificationLog.Channel.SMS, NotificationLog.Channel.EMAIL, NotificationLog.Channel.PUSH}
        )
        
        security_logs = logs.filter(recipient=self.security_user)
        self.assertEqual(security_logs.count(), 2)
        self.assertEqual(
            set(security_logs.values_list('channel', flat=True)),
            {NotificationLog.Channel.IN_APP, NotificationLog.Channel.PUSH}
        )
        
        volunteer_logs = logs.filter(recipient=self.volunteer_user)
        self.assertEqual(volunteer_logs.count(), 2)
        self.assertEqual(
            set(volunteer_logs.values_list('channel', flat=True)),
            {NotificationLog.Channel.IN_APP, NotificationLog.Channel.PUSH}
        )

    def test_alert_visibility_permissions(self):
        # Trigger an alert
        alert = SOSAlert.objects.create(
            resident=self.resident,
            category="SECURITY",
            message="Suspicious person outside flat",
            status="OPEN"
        )
        
        # 1. Resident can view their own alert
        self.client.force_authenticate(user=self.resident)
        response = self.client.get(reverse('sosalert-detail', kwargs={'pk': alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Guardian can view the alert because they are in the resident's emergency contacts
        self.client.force_authenticate(user=self.guardian)
        response = self.client.get(reverse('sosalert-detail', kwargs={'pk': alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Security can view the alert
        self.client.force_authenticate(user=self.security_user)
        response = self.client.get(reverse('sosalert-detail', kwargs={'pk': alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Another random resident cannot view this alert
        other_resident = User.objects.create_user(
            username="other_resident",
            email="other@example.com",
            password="Password123!",
            phone_number="7777777777",
            age=29,
            role="RESIDENT"
        )
        self.client.force_authenticate(user=other_resident)
        response = self.client.get(reverse('sosalert-detail', kwargs={'pk': alert.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
