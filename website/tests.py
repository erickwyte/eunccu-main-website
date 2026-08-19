from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from website.admin import TestimonyAdmin
from website.models import Notification, Testimony, BibleStudySemester, BibleStudyEnrollment
from website.permissions import USER_MANAGER_GROUP


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
            completed=True,
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

    def test_user_manager_group_exists_and_dashboard_is_accessible(self):
        self.assertTrue(Group.objects.filter(name=USER_MANAGER_GROUP).exists())

        user_manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            password='secret123',
            full_name='User Manager',
            phone=111222333,
        )
        user_manager.groups.add(Group.objects.get(name=USER_MANAGER_GROUP))

        self.client.force_login(user_manager)
        response = self.client.get(reverse('website:user_manager_dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_superuser_can_access_user_manager_dashboard(self):
        super_admin = User.objects.create_superuser(
            email='superadmin@example.com',
            username='superadmin',
            password='secret123',
            full_name='Super Admin',
            phone=999888777,
        )

        self.client.force_login(super_admin)
        response = self.client.get(reverse('website:user_manager_dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_complete_registration_token_logs_user_in(self):
        pending_user = User.objects.create_user(
            email='tokenuser@example.com',
            username='tokenuser',
            password='secret123',
            full_name='Token User',
            is_active=True,
            completed=False,
            must_change_password=True,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(pending_user.pk))
        token = default_token_generator.make_token(pending_user)

        response = self.client.get(
            reverse('website:complete_registration_token', kwargs={'uidb64': uidb64, 'token': token})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Your Registration')

    def test_profile_shows_bible_study_enroll_button_when_active(self):
        BibleStudySemester.objects.create(
            name='Semester 1 2026',
            start_date='2026-01-05',
            end_date='2026-05-30',
            is_active=True,
            registration_open=True,
        )

        self.client.force_login(self.member_user)
        response = self.client.get(reverse('website:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enroll for Bible Study')
        self.assertContains(response, reverse('website:bible_study_enroll'))

    def test_active_bible_study_enrollment_creates_record(self):
        semester = BibleStudySemester.objects.create(
            name='Semester 1 2026',
            start_date='2026-01-05',
            end_date='2026-05-30',
            is_active=True,
            registration_open=True,
        )

        self.member_user.completed = True
        self.member_user.save(update_fields=['completed'])

        self.client.force_login(self.member_user)
        response = self.client.post(reverse('website:bible_study_enroll'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            BibleStudyEnrollment.objects.filter(
                user=self.member_user,
                semester=semester,
            ).exists()
        )

    def test_user_manager_users_are_redirected_from_admin(self):
        user_manager = User.objects.create_user(
            email='admin-blocked@example.com',
            username='adminblocked',
            password='secret123',
            full_name='Restricted Manager',
            phone=444555666,
            is_staff=False,
            is_superuser=False,
        )
        user_manager.groups.add(Group.objects.get(name=USER_MANAGER_GROUP))

        self.client.force_login(user_manager)
        response = self.client.get('/admin/', follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('website:user_manager_dashboard'))
