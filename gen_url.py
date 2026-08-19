#!/usr/bin/env python3
"""Generate a test registration URL"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Get a test user and generate a new link
users = User.objects.filter(must_change_password=True)[:1]
if users.exists():
    user = users.first()
    from auth_utils.views import generate_onboarding_url
    url = generate_onboarding_url(user)
    print(f"Test URL for {user.email}:")
    print(f"http://localhost:8000{url}")
else:
    print("No users with must_change_password=True found")
    # List all users
    all_users = User.objects.all()[:5]
    for u in all_users:
        print(f"- {u.email}: must_change_password={u.must_change_password}")
