import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Delete old admin if needed
User.objects.filter(email='websitemanager@eunccu.org').delete()

# Create new superuser
User.objects.create_superuser(email='websitemanager@eunccu.org', username='admin', password='Admin@2026')
print('New superuser created: websitemanager@eunccu.org / Admin@2026')