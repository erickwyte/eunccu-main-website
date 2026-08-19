#!/usr/bin/env python3
"""Create a test user for registration using SQLite"""
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.test_settings')  # Use test settings with SQLite
django.setup()

from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

# Try to find an existing incomplete user
test_user = User.objects.filter(completed=False).first()

if not test_user:
    # Create a new test user
    test_user = User.objects.create_user(
        email='testuser@eunccu.org',
        username='testuser789',
        full_name='Test User',
        completed=False,
        is_active=True
    )
    print(f"✓ Created new test user: {test_user.email}")
else:
    print(f"✓ Found existing test user: {test_user.email}")

# Generate registration link
uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
token = default_token_generator.make_token(test_user)
registration_url = f"/complete-registration/{uidb64}/{token}/"

print(f"\n╔════════════════════════════════════════════════════════╗")
print(f"║          REGISTRATION LINK GENERATED                  ║")
print(f"╚════════════════════════════════════════════════════════╝")
print(f"\n🔗 URL: http://localhost:8000{registration_url}")
print(f"\n📧 Email: {test_user.email}")
print(f"🔐 Username: {test_user.username}")
print(f"✓ Completed: {test_user.completed}")
print(f"\nThis user can now access the complete registration form!")
