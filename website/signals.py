from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Event, Notification, CustomUser
from django.conf import settings
from website.utils import schedule_notification_task, send_html_email
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.conf import settings
from .models import Event, Notification, CustomUser

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def send_welcome_email_on_user_create(sender, instance, created, **kwargs):
    if created and instance.email and getattr(instance, '_send_welcome_email', True):
        try:
            send_html_email(
                subject='Welcome to EUNCCU – Your Account Has Been Created',
                to_email=instance.email,
                template_name='website/emails/onboarding_email.html',
                context={
                    'user': instance,
                    'temp_password': getattr(settings, 'DEFAULT_TEMP_PASSWORD', 'student'),
                    'login_url': f"{getattr(settings, 'SITE_URL', 'https://eunccu.org')}/login/",
                },
            )
        except Exception:
            logger.exception('Welcome email failed for %s', instance.email)


@receiver(post_save, sender=Event)
def notify_users_on_event_create(sender, instance, created, **kwargs):
    if created:
        schedule_notification_task(
            lambda event_id=instance.pk: send_event_notifications_bulk(event_id)
        )

def send_event_notifications_bulk(event_id):
    event_instance = Event.objects.filter(pk=event_id).first()
    if not event_instance:
        return

    users = CustomUser.objects.all()
    event_name = event_instance.event_name

    notifications = [
        Notification(
            user=user,
            message=f"New event posted: {event_name}"
        )
        for user in users
    ]
    Notification.objects.bulk_create(notifications)

    messages = []
    for user in users:
        messages.append((
            "New Event Posted",
            f"Hello {user.username},\n\nA new event has been posted: {event_name}.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        ))

    send_mass_mail(messages, fail_silently=True)

def send_event_notifications(event_instance):
    users = CustomUser.objects.all()

    for user in users:
        Notification.objects.create(
            user=user,
            message=f"New event posted: {event_instance.event_name}"
        )

        send_mail(
            subject="New Event Posted",
            message=f"Hello {user.username},\n\nA new event has been posted: {event_instance.event_name}. Check it out on the website!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )


