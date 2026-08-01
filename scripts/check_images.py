import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
django.setup()

from django.conf import settings
from website.models import Image

print('MEDIA_URL=', settings.MEDIA_URL)
print('MEDIA_ROOT=', settings.MEDIA_ROOT)

qs = Image.objects.all()
print('IMAGE_COUNT=', qs.count())

for i in qs:
    name = i.image.name if hasattr(i.image, 'name') else str(i.image)
    url = getattr(i.image, 'url', 'NO_URL')
    exists = os.path.exists(os.path.join(settings.MEDIA_ROOT, name))
    print(f"ID={i.id} name={name} url={url} exists={exists}")
