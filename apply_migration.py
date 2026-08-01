import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
import django
django.setup()
from django.db import connection
from django.core.management import call_command

call_command('migrate', 'website', '0015')
