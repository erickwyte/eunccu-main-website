# website/decorators.py
"""
Custom access-control decorators for the User Manager dashboard.

Usage (function-based views):
    from website.decorators import user_manager_required

    @user_manager_required
    def my_view(request):
        ...

Usage (class-based views): use UserManagerMixin defined in this module or
import it from here for consistency.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import AccessMixin

from .permissions import is_user_manager


def user_manager_required(view_func):
    """
    Decorator that restricts a view to members of the 'User Manager' group.

    - Unauthenticated users are sent to the login page.
    - Authenticated users without the required group receive a 403-style
      message and are redirected to the home page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please sign in to access this page.')
            return redirect('website:login')

        if not (request.user.is_superuser or is_user_manager(request.user)):
            messages.error(
                request,
                'You do not have permission to access this area.'
            )
            return redirect('website:home')

        return view_func(request, *args, **kwargs)

    return wrapper


class UserManagerMixin(AccessMixin):
    """
    CBV mixin equivalent of @user_manager_required.

    Inherit this mixin before any other class in your CBV hierarchy.
    Example:
        class MyDashboardView(UserManagerMixin, TemplateView):
            ...
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please sign in to access this page.')
            return redirect('website:login')

        if not (request.user.is_superuser or is_user_manager(request.user)):
            messages.error(
                request,
                'You do not have permission to access this area.'
            )
            return redirect('website:home')

        return super().dispatch(request, *args, **kwargs)
