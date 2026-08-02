import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from website.views import CreateUserView
from django.urls import reverse

factory = RequestFactory()
user = get_user_model().objects.filter(is_superuser=True).first()
print('superuser:', user)
req = factory.post(reverse('website:user_manager_create'), {
    'full_name': 'Test User',
    'email': 'testuser@example.com',
})
req.user = user
SessionMiddleware(lambda request: None).process_request(req)
req.session.save()
req._messages = FallbackStorage(req)

try:
    response = CreateUserView.as_view()(req)
    print('response status', getattr(response, 'status_code', None))
except Exception:
    traceback.print_exc()
