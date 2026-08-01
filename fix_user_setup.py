import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
import django
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

with connection.cursor() as cursor:
    cursor.execute("ALTER TABLE website_customuser ADD COLUMN IF NOT EXISTS completed BOOLEAN NOT NULL DEFAULT FALSE")
    cursor.execute("ALTER TABLE website_customuser ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT TRUE")

User = get_user_model()
email = 'admin@example.com'
username = 'admin'
password = 'Admin123!'

user = User.objects.filter(email=email).first()
if not user:
    user = User.objects.create_superuser(email=email, username=username, password=password)

print('user_exists=' + str(user is not None))
print('email=' + user.email)
print('username=' + user.username)
print('is_staff=' + str(user.is_staff))
print('is_superuser=' + str(user.is_superuser))
