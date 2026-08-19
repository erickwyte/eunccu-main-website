"""Management command: setup_weekly_backup_cron

Installs a weekly cron job that runs the backup_to_drive command.

Usage:
    python manage.py setup_weekly_backup_cron

Optional arguments:
    --day-of-week    Day of week for the backup (mon,tue,wed,thu,fri,sat,sun). Default: sun
    --hour           Hour of day in 24-hour format. Default: 2
    --minute         Minute of the hour. Default: 0
    --timezone       Time zone for the schedule. Default: Africa/Nairobi (East Africa Time)
    --command        Optional extra arguments to pass to backup_to_drive.
"""

import os
import sys
import platform
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings

try:
    from crontab import CronTab
except ImportError:
    CronTab = None


class Command(BaseCommand):
    help = "Install a weekly cron job to run the backup_to_drive command."

    def add_arguments(self, parser):
        parser.add_argument(
            '--day-of-week',
            default='sun',
            choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            help='Day of week to run the backup. Default is sun.',
        )
        parser.add_argument(
            '--hour',
            type=int,
            default=2,
            help='Hour of day in 24-hour format. Default is 2.',
        )
        parser.add_argument(
            '--minute',
            type=int,
            default=0,
            help='Minute of the hour. Default is 0.',
        )
        parser.add_argument(
            '--timezone',
            default=getattr(settings, 'TIME_ZONE', 'Africa/Nairobi'),
            help='Time zone to schedule the backup in. Default is Africa/Nairobi.',
        )
        parser.add_argument(
            '--command',
            default='',
            help='Additional arguments to append to the backup_to_drive command.',
        )

    def handle(self, *args, **options):
        if CronTab is None:
            self.stdout.write(self.style.ERROR(
                'python-crontab is not installed. Install it with pip install python-crontab.'
            ))
            return

        python_executable = sys.executable
        project_dir = os.path.abspath(settings.BASE_DIR)
        manage_py = os.path.join(project_dir, 'manage.py')
        if not os.path.exists(manage_py):
            self.stdout.write(self.style.ERROR(f'Manage.py not found at {manage_py}'))
            return

        backup_cmd = f'{python_executable} {manage_py} backup_to_drive'
        if options['command']:
            backup_cmd += ' ' + options['command']

        timezone = options['timezone']
        quoted_timezone = timezone.replace('"', '\\"')
        cron_command = f'cd {project_dir} && TZ={quoted_timezone} {backup_cmd}'

        job_comment = 'weekly_backup_to_drive'

        if platform.system().lower().startswith('windows'):
            self.stdout.write(self.style.WARNING(
                'Installing as a Windows scheduled task.'
            ))

            action = sys.executable
            argument = f'"{manage_py}" backup_to_drive --use-backup-account --drive-auth-method oauth'
            task_name = 'EUNCCU Backup'
            task_description = 'Weekly EUNCCU database backup'
            day_of_week = options['day_of_week'].capitalize()
            time_str = f'{options["hour"]}:{options["minute"]:02d}'

            ps_command = (
                f"$Action = New-ScheduledTaskAction -Execute '{action}' -Argument '{argument}' ; "
                f"$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {day_of_week} -At (Get-Date '{time_str}') ; "
                f"Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName '{task_name}' -Description '{task_description}'"
            )

            try:
                subprocess.run(['powershell.exe', '-NoProfile', '-Command', ps_command], check=True)
                self.stdout.write(self.style.SUCCESS(
                    f'Windows scheduled task "{task_name}" installed to run weekly on {day_of_week} at {time_str}.')
                )
            except subprocess.CalledProcessError as e:
                self.stdout.write(self.style.ERROR(
                    'Failed to install Windows scheduled task. Run the following command manually:'
                ))
                self.stdout.write(ps_command)
            return

        if CronTab is None:
            self.stdout.write(self.style.ERROR(
                'python-crontab is not installed. Install it with pip install python-crontab.'
            ))
            return

        cron = CronTab(user=True)

        # Remove existing jobs with the same comment.
        for job in cron.find_comment(job_comment):
            cron.remove(job)

        job = cron.new(command=cron_command, comment=job_comment)
        job.setall(f'{options["minute"]} {options["hour"]} * * {options["day_of_week"]}')

        if not job.is_valid():
            self.stdout.write(self.style.ERROR('Generated cron job is not valid.'))
            return

        cron.write()
        self.stdout.write(self.style.SUCCESS(
            f'Weekly backup cron job installed: {job}. Run at {options["day_of_week"]} {options["hour"]}:{options["minute"]:02d} in {timezone}.'
        ))
