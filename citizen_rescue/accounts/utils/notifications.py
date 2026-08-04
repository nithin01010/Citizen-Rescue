import logging
from django.core.mail import send_mail
from accounts.models import NotificationLog, EmergencyContact, SecurityProfile, VolunteerProfile

logger = logging.getLogger(__name__)


def send_sms(phone_number, message):
    """
    Simulates sending an SMS notification.
    In production, this would integrate with a provider like Twilio.
    """
    return True


def send_push_notification(recipient, title, message):
    """
    Simulates sending a push notification (Firebase Cloud Messaging / WebPush).
    In production, this would use firebase-admin SDK.
    """
    return True


def send_email(email, subject, body):
    """
    Simulates sending an email notification.
    """
    return True


def send_alert_notifications(alert):
    """
    Routes an SOS alert to all relevant recipients via configured channels.
    Recipients:
      - Primary Guardians: SMS, Email, In-App, Push
      - On-Duty Security: In-App, Push
      - Available Volunteers: In-App, Push
    """
    resident = alert.resident
    category_display = alert.get_category_display()

    # Define notification contents
    subject = f"EMERGENCY: {category_display} alert triggered by {resident.username}"
    message_body = (
        f"SOS Alert!\n"
        f"Resident: {resident.username}\n"
        f"Category: {category_display}\n"
        f"Message: {alert.message or 'No message provided'}\n"
        f"Location: Latitude {alert.latitude}, Longitude {alert.longitude}\n"
        f"Time: {alert.created_at}"
    )

    # 1. Notify Guardians
    guardian_contacts = EmergencyContact.objects.filter(
        resident=resident,
        priority=EmergencyContact.Priority.PRIMARY
    )
    for contact in guardian_contacts:
        guardian_user = contact.guardian

        # In-App Notification
        NotificationLog.objects.create(
            alert=alert,
            recipient=guardian_user,
            channel=NotificationLog.Channel.IN_APP,
            status=NotificationLog.DeliveryStatus.DELIVERED
        )

        # SMS Notification
        sms_success, sms_err = send_sms(contact.phone_number, message_body)
        NotificationLog.objects.create(
            alert=alert,
            recipient=guardian_user,
            channel=NotificationLog.Channel.SMS,
            status=NotificationLog.DeliveryStatus.DELIVERED if sms_success else NotificationLog.DeliveryStatus.FAILED,
            error_message=sms_err
        )

        # Email Notification
        email_success, email_err = send_email(guardian_user.email, subject, message_body)
        NotificationLog.objects.create(
            alert=alert,
            recipient=guardian_user,
            channel=NotificationLog.Channel.EMAIL,
            status=NotificationLog.DeliveryStatus.DELIVERED if email_success else NotificationLog.DeliveryStatus.FAILED,
            error_message=email_err
        )

        # Push Notification
        push_success, push_err = send_push_notification(guardian_user, subject, message_body)
        NotificationLog.objects.create(
            alert=alert,
            recipient=guardian_user,
            channel=NotificationLog.Channel.PUSH,
            status=NotificationLog.DeliveryStatus.DELIVERED if push_success else NotificationLog.DeliveryStatus.FAILED,
            error_message=push_err
        )

    # 2. Notify Security Personnel (on duty)
    security_profiles = SecurityProfile.objects.filter(on_duty=True)
    for profile in security_profiles:
        security_user = profile.user

        # In-App Notification
        NotificationLog.objects.create(
            alert=alert,
            recipient=security_user,
            channel=NotificationLog.Channel.IN_APP,
            status=NotificationLog.DeliveryStatus.DELIVERED
        )

        # Push Notification
        push_success, push_err = send_push_notification(security_user, subject, message_body)
        NotificationLog.objects.create(
            alert=alert,
            recipient=security_user,
            channel=NotificationLog.Channel.PUSH,
            status=NotificationLog.DeliveryStatus.DELIVERED if push_success else NotificationLog.DeliveryStatus.FAILED,
            error_message=push_err
        )

    # 3. Notify Volunteers (available)
    volunteer_profiles = VolunteerProfile.objects.filter(is_available=True)
    for profile in volunteer_profiles:
        volunteer_user = profile.user

        # In-App Notification
        NotificationLog.objects.create(
            alert=alert,
            recipient=volunteer_user,
            channel=NotificationLog.Channel.IN_APP,
            status=NotificationLog.DeliveryStatus.DELIVERED
        )

        # Push Notification
        push_success, push_err = send_push_notification(volunteer_user, subject, message_body)
        NotificationLog.objects.create(
            alert=alert,
            recipient=volunteer_user,
            channel=NotificationLog.Channel.PUSH,
            status=NotificationLog.DeliveryStatus.DELIVERED if push_success else NotificationLog.DeliveryStatus.FAILED,
            error_message=push_err
        )
