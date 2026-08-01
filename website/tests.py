from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse

from website.admin import TestimonyAdmin
from website.models import Notification, Testimony


User = get_user_model()


class TestimonyWorkflowTests(TestCase):
    TEST_IMAGE_BYTES = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
        b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00'
        b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01'
        b'\x00\x3b'
    )

    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='secret123',
            role='developer',
            is_staff=True,
            full_name='Site Admin',
            phone=123456789,
        )
        self.member_user = User.objects.create_user(
            email='member@example.com',
            username='member',
            password='secret123',
            full_name='Test Member',
            phone=987654321,
        )

    @patch('website.views.get_latest_youtube_video', return_value=(None, None))
    def test_homepage_shows_only_approved_testimonies(self, _mock_video):
        Testimony.objects.create(
            testimony_giver='Approved User',
            position='Member',
            testimony='Approved testimony content',
            is_approved=True,
        )
        Testimony.objects.create(
            testimony_giver='Pending User',
            position='Member',
            testimony='Pending testimony content',
            is_approved=False,
        )

        response = self.client.get(reverse('website:home'))

        self.assertContains(response, 'Approved testimony content')
        self.assertNotContains(response, 'Pending testimony content')

    def test_authenticated_user_can_submit_testimony_and_notify_admins(self):
        self.client.force_login(self.member_user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse('website:submit_testimony'),
                {
                    'testimony': 'God has been faithful throughout this semester.',
                    'image': SimpleUploadedFile(
                        'testimony.gif',
                        self.TEST_IMAGE_BYTES,
                        content_type='image/gif',
                    ),
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('website:home'))
        testimony = Testimony.objects.get(submitted_by=self.member_user)
        self.assertEqual(testimony.testimony_giver, 'Test Member')
        self.assertEqual(testimony.position, 'Member')
        self.assertFalse(testimony.is_approved)

        admin_notification = Notification.objects.get(user=self.admin_user)
        self.assertIn('needs review', admin_notification.message)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.admin_user.email, mail.outbox[0].to)
        self.assertIn('needs admin review', mail.outbox[0].body)

    def test_admin_approval_notifies_submitter(self):
        testimony = Testimony.objects.create(
            testimony_giver='Test Member',
            position='Member',
            testimony='A pending testimony.',
            submitted_by=self.member_user,
            is_approved=False,
        )
        testimony_admin = TestimonyAdmin(Testimony, AdminSite())
        request = self.factory.post('/admin/website/testimony/')
        request.user = self.admin_user

        with self.captureOnCommitCallbacks(execute=True):
            testimony.is_approved = True
            testimony_admin.save_model(request, testimony, form=None, change=True)

        testimony.refresh_from_db()
        self.assertTrue(testimony.is_approved)
        self.assertIsNotNone(testimony.reviewed_at)
        self.assertTrue(
            Notification.objects.filter(
                user=self.member_user,
                message__icontains='approved',
            ).exists()
        )
