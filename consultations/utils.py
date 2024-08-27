from django.conf import settings
from django.core.mail import send_mail


def send_consultation_notification(consultation):
    subject = "Consultation Notification"
    message = f"Your consultation with {consultation.slot.specialist.user.username} is scheduled for {consultation.slot.start_time}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [consultation.client.email]
    send_mail(subject, message, from_email, recipient_list)


def send_cancellation_notification(consultation):
    subject = "Consultation Cancellation"
    message = f"Your consultation with {consultation.slot.specialist.user.username} has been cancelled. Reason: {consultation.cancellation_reason}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [consultation.client.email]
    send_mail(subject, message, from_email, recipient_list)
