# website/middleware.py
"""
ProfileCompletionMiddleware
----------------------------
Intercepts every authenticated request and enforces the profile-completion
flow. Users whose `completed` flag is False are redirected to the
complete-registration page until they finish onboarding.

Bypass paths (never redirected):
  - /login/
  - /logout/
  - /complete-registration/
  - /static/        (static files)
  - /media/         (uploaded media)
  - /admin/         (Django admin, not used for this workflow)
  - /auth/          (password-reset endpoints)
  - /ckeditor5/     (editor file uploads)
"""

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    """
    Redirects authenticated users with an incomplete profile to the
    complete-registration page. All other requests pass through unchanged.
    """

    # URL path prefixes that are always allowed through, regardless of
    # profile completion status.
    EXEMPT_PREFIXES = (
        '/login/',
        '/logout/',
        '/complete-registration/',
        '/static/',
        '/media/',
        '/media-files/',
        '/admin/',
        '/auth/',
        '/ckeditor5/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only intervene for authenticated users.
        if request.user.is_authenticated:
            path = request.path_info

            # Check whether this path is exempt from the redirect.
            is_exempt = any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES)

            if not is_exempt:
                # Superusers and staff bypass the completion requirement so
                # they can always access the system.
                if not request.user.is_superuser and not request.user.is_staff:
                    if not request.user.completed:
                        complete_url = '/complete-registration/'
                        if path != complete_url:
                            return redirect(complete_url)

        return self.get_response(request)
