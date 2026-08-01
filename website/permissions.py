# website/permissions.py
"""
Centralised permission helpers for group-based access control.

Use these helpers instead of checking is_staff or is_superuser so that
the access rules remain in one place and are easy to adjust later.
"""

from django.contrib.auth.models import Group


USER_MANAGER_GROUP = 'User Manager'


def is_user_manager(user):
    """
    Return True if the given user belongs to the 'User Manager' group.

    This is the single source of truth for User Manager access checks.
    Used by both the function-based decorator and the CBV mixin.
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=USER_MANAGER_GROUP).exists()


def ensure_user_manager_group_exists():
    """
    Idempotently creates the 'User Manager' Django group.
    Safe to call multiple times (e.g. from AppConfig.ready or a management command).
    Returns the group instance.
    """
    group, created = Group.objects.get_or_create(name=USER_MANAGER_GROUP)
    return group
