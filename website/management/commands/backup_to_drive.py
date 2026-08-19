"""Management command: backup_to_drive

Creates a database dump and uploads it to Google Drive.

Usage:
    python manage.py backup_to_drive

Optional environment variables:
    BACKUP_FILE_DIR - local directory to store backup files (default: BASE_DIR/backups)
    GOOGLE_DRIVE_BACKUP_FOLDER_ID - optional Drive folder ID for backup uploads
    GOOGLE_BACKUP_DRIVE_AUTH_METHOD - 'service_account' or 'oauth' (default: service_account)
    GOOGLE_BACKUP_OAUTH_CLIENT_SECRETS_FILE - client secrets JSON file for OAuth uploads
    GOOGLE_BACKUP_OAUTH_TOKEN_FILE - OAuth token storage file (default: google_drive_backup_token.json)
"""

import gzip
import os
import shutil
import subprocess
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from website.google_drive_utils import upload_file_to_drive


class Command(BaseCommand):
    help = "Create a database backup and upload it to Google Drive."

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-upload',
            action='store_true',
            help='Create the backup locally but do not upload to Google Drive.',
        )
        parser.add_argument(
            '--drive-auth-method',
            choices=['service_account', 'oauth'],
            help='Override Google Drive auth method for this run.',
        )
        parser.add_argument(
            '--use-backup-account',
            action='store_true',
            help='Use the backup-specific Drive/auth settings for uploads.',
        )

    def handle(self, *args, **options):
        backup_dir = os.environ.get('BACKUP_FILE_DIR', os.path.join(settings.BASE_DIR, 'backups'))
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_filename = f"db_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)

        self.stdout.write(f"Creating backup file: {backup_path}")

        db_settings = settings.DATABASES.get('default', {})
        engine = db_settings.get('ENGINE', '')

        db_name = db_settings.get('NAME')
        db_user = db_settings.get('USER')
        db_password = db_settings.get('PASSWORD')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = str(db_settings.get('PORT', ''))

        env = os.environ.copy()
        dump_command = []

        if 'postgresql' in engine.lower() or 'postgres' in engine.lower():
            if db_password:
                env['PGPASSWORD'] = db_password
            dump_command = [
                'pg_dump',
                '--format=plain',
                '--no-owner',
                '--no-privileges',
                '--dbname', db_name,
                '--username', db_user,
                '--host', db_host,
                '--port', db_port,
                '--file', backup_path,
            ]
        elif 'mysql' in engine.lower():
            if db_password:
                env['MYSQL_PWD'] = db_password
            dump_command = [
                'mysqldump',
                '--routines',
                '--events',
                '--single-transaction',
                '--skip-lock-tables',
                '--host', db_host,
                '--port', db_port,
                '--user', db_user,
                db_name,
            ]
        else:
            self.stdout.write(self.style.ERROR('This backup command currently supports only PostgreSQL and MySQL.'))
            return

        try:
            subprocess.check_call(dump_command, env=env)
        except FileNotFoundError:
            if 'mysql' in engine.lower():
                self.stdout.write(self.style.ERROR('mysqldump is not installed or not available in PATH.'))
            else:
                self.stdout.write(self.style.ERROR('pg_dump is not installed or not available in PATH.'))
            return
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Database dump failed with exit code {e.returncode}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Backup file created successfully: {backup_path}'))

        compressed_path = f"{backup_path}.gz"
        self.stdout.write(f"Compressing backup file to: {compressed_path}")

        try:
            with open(backup_path, 'rb') as raw_file, gzip.open(compressed_path, 'wb') as compressed_file:
                shutil.copyfileobj(raw_file, compressed_file)
            os.remove(backup_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to compress backup file: {e}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Compressed backup file created successfully: {compressed_path}'))

        if options['no_upload']:
            return

        drive_folder_id = getattr(settings, 'GOOGLE_DRIVE_BACKUP_FOLDER_ID', None) or getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', None)
        if not drive_folder_id:
            self.stdout.write(self.style.ERROR('GOOGLE_DRIVE_BACKUP_FOLDER_ID or GOOGLE_DRIVE_FOLDER_ID must be configured to upload backups to Google Drive.'))
            return

        self.stdout.write('Uploading backup to Google Drive...')
        uploaded_file = upload_file_to_drive(
            compressed_path,
            folder_id=drive_folder_id,
            use_backup_account=options['use_backup_account'],
            auth_method=options.get('drive_auth_method'),
        )

        if uploaded_file:
            self.stdout.write(self.style.SUCCESS(f"Backup uploaded to Google Drive (id={uploaded_file.get('id')})."))
        else:
            self.stdout.write(self.style.ERROR(
                'Backup upload failed. Ensure the backup folder is configured correctly, and the chosen auth method has access.'
            ))

        keep_count = int(os.environ.get('BACKUP_RETAIN_COUNT', 30))
        if keep_count > 0:
            backup_files = sorted([
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if f.endswith('.sql.gz')
            ], key=os.path.getmtime)
            old_files = backup_files[:-keep_count]
            for old_file in old_files:
                try:
                    os.remove(old_file)
                except Exception:
                    pass
