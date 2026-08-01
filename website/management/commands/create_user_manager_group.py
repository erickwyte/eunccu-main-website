# website/management/commands/create_user_manager_group.py
"""
Management command: create_user_manager_group

Creates the 'User Manager' Django Group if it does not already exist.
Run this once after initial migration:

    python manage.py create_user_manager_group
"""

from django.core.management.base import BaseCommand

from website.permissions import ensure_user_manager_group_exists


class Command(BaseCommand):
    help = "Creates the 'User Manager' group if it does not already exist."

    def handle(self, *args, **options):
        group = ensure_user_manager_group_exists()
        # get_or_create returns (instance, created); we check if it is new.
        if group.pk:
            self.stdout.write(
                self.style.SUCCESS(
                    f"'User Manager' group is ready (id={group.pk})."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Could not create or retrieve the 'User Manager' group.")
            )
