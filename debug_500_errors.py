#!/usr/bin/env python
"""
Debug script for 500 errors on ALL pages
Run this on your production server to identify the issue
Checks: Gallery, Devotions, Ministries, Leadership, Events, Home, etc.
"""

import os
import django
import sys
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError

print("=" * 70)
print("DEBUGGING 500 ERRORS - ALL PAGES COMPREHENSIVE CHECK")
print("=" * 70)

# Test 1: Database Connection
print("\n[TEST 1] Database Connection")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection: OK")
except OperationalError as e:
    print(f"❌ Database connection FAILED: {e}")
    sys.exit(1)

# Define all models that are queried
models_to_check = [
    ('Image', 'website_image', 'Gallery page'),
    ('Devotion', 'website_devotion', 'Devotions page'),
    ('Ministry', 'website_ministry', 'Ministries page'),
    ('Eteam', 'website_eteam', 'Ministries page'),
    ('Class', 'website_class', 'Ministries page'),
    ('SpecialCommittee', 'website_specialcommittee', 'Ministries page'),
    ('Exec', 'website_exec', 'Leadership page'),
    ('Leader', 'website_leader', 'Leadership page'),
    ('Event', 'website_event', 'Events & Home page'),
    ('Testimony', 'website_testimony', 'Home page'),
    ('SemesterTheme', 'website_semestertheme', 'Home page'),
    ('BibleStudySemester', 'website_biblestudysemester', 'Home page'),
    ('BibleStudyEnrollment', 'website_biblestudyenrollment', 'Profile page'),
]

print(f"\n[TEST 2] Checking {len(models_to_check)} Model Tables")
print("-" * 70)

missing_tables = []
for model_name, table_name, used_on in models_to_check:
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {model_name:25} ({table_name:30}) - {count} records - Used on: {used_on}")
    except Exception as e:
        print(f"  ❌ {model_name:25} ({table_name:30}) - MISSING - Used on: {used_on}")
        missing_tables.append((table_name, model_name))

# Test 3: Try all model queries
print(f"\n[TEST 3] Testing Model Queries ({len(models_to_check)} models)")
print("-" * 70)

from website.models import (
    Image, Devotion, Ministry, Eteam, Class, SpecialCommittee,
    Exec, Leader, Event, Testimony, SemesterTheme, BibleStudySemester,
    BibleStudyEnrollment
)

query_tests = [
    ('Image', lambda: Image.objects.filter(image_to_show_on_website=True).order_by('-uploaded_at')),
    ('Devotion', lambda: Devotion.objects.filter(is_published=True).order_by('-published_date')),
    ('Ministry', lambda: Ministry.objects.all()),
    ('Eteam', lambda: Eteam.objects.all()),
    ('Class', lambda: Class.objects.all()),
    ('SpecialCommittee', lambda: SpecialCommittee.objects.all()),
    ('Exec', lambda: Exec.objects.all().order_by('-id')),
    ('Leader', lambda: Leader.objects.all()),
    ('Event', lambda: Event.objects.all().order_by('-start_date')),
    ('Testimony', lambda: Testimony.objects.filter(is_approved=True).order_by('-reviewed_at')),
    ('SemesterTheme', lambda: SemesterTheme.objects.filter(is_active=True).first()),
    ('BibleStudySemester', lambda: BibleStudySemester.objects.filter(is_active=True).first()),
]

failed_queries = []
for model_name, query_func in query_tests:
    try:
        result = query_func()
        if hasattr(result, 'count'):
            count = result.count()
        else:
            count = 1 if result else 0
        print(f"  ✅ {model_name:25} query successful - {count} results")
    except Exception as e:
        print(f"  ❌ {model_name:25} query FAILED: {str(e)[:50]}")
        failed_queries.append((model_name, str(e)))

# Summary
print("\n" + "=" * 70)
if not missing_tables and not failed_queries:
    print("✅ ALL CHECKS PASSED - No database issues detected!")
    print("=" * 70)
else:
    print("❌ ISSUES DETECTED")
    print("=" * 70)
    if missing_tables:
        print(f"\n📋 Missing Tables ({len(missing_tables)}):")
        for table, model in missing_tables:
            print(f"   - {table} ({model})")
        print("\n💡 FIX: Run 'python manage.py migrate'")
    
    if failed_queries:
        print(f"\n📋 Failed Queries ({len(failed_queries)}):")
        for model, error in failed_queries:
            print(f"   - {model}: {error[:60]}")
        print("\n💡 FIX: Check database schema or run 'python manage.py migrate'")

print("\n" + "=" * 70)
