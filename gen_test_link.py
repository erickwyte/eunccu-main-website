#!/usr/bin/env python3
"""Create a test user and generate registration link"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

User = get_user_model()

# Try to find an existing user with must_change_password or not completed
test_user = User.objects.filter(must_change_password=True).first()

if not test_user:
    # Try to find any user who hasn't completed registration
    test_user = User.objects.filter(completed=False).first()

if not test_user:
    # Create a new test user
    test_user = User.objects.create_user(
        email='testuser@eunccu.test',
        username='testuser_123',
        full_name='Test User',
        must_change_password=True,
        completed=False,
        is_active=True
    )
    print(f"✓ Created new test user: {test_user.email}")
else:
    print(f"✓ Using existing test user: {test_user.email}")

# Generate registration link
uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
token = default_token_generator.make_token(test_user)
registration_url = f"/complete-registration/{uidb64}/{token}/"

print(f"\n--- REGISTRATION LINK ---")
print(f"http://localhost:8000{registration_url}")
print(f"\n--- USER INFO ---")
print(f"Email: {test_user.email}")
print(f"Username: {test_user.username}")
print(f"Completed: {test_user.completed}")
print(f"Must Change Password: {test_user.must_change_password}")
