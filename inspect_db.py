import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
import django
django.setup()
from django.db import connection

cursor = connection.cursor()
print('tables=', connection.introspection.table_names(cursor))
print('has_customuser=', 'website_customuser' in connection.introspection.table_names(cursor))
if 'website_customuser' in connection.introspection.table_names(cursor):
    cols = [c.name for c in connection.introspection.get_columns(cursor, 'website_customuser')]
    print('columns=', cols)
