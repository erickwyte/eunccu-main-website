# union/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls', namespace='website')),
    path('auth/', include('auth_utils.urls', namespace='auth_utils')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Serve static and media files in development
import sys

# Serve static and media files when running the development server.
# This uses the local static directories directly rather than relying on collected static files.
if settings.DEBUG or 'runserver' in sys.argv:
    if getattr(settings, 'STATICFILES_DIRS', None):
        for static_dir in settings.STATICFILES_DIRS:
            urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
    else:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ensure media files are at least reachable from the dev server.
# In production a proper media-serving setup should be used instead.
try:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
except Exception:
    # If static() cannot be used for any reason, skip silently.
    pass