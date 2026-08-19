# Bible Study Integration Guide

## Overview
The Bible Study app will connect to the same database and authentication system as the main EUNCCU website. This document provides the configuration needed to connect them.

## Prerequisites

1. Main EUNCCU website is deployed and running
2. Bible Study project is available on your server
3. Both apps can access the same MySQL database
4. Both domains are set up (eunccu.org and biblestudy.eunccu.org)

## Configuration Steps

### 1. Database Configuration (Bible Study)

In Bible Study's `settings.py`, set the database to point to the main site's database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eunccu_production_db',  # SAME as main site
        'USER': 'eunccu_prod_user',      # SAME as main site
        'PASSWORD': 'your-db-password',  # SAME as main site
        'HOST': 'your-mysql-host.com',   # SAME as main site
        'PORT': 3306,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
            'charset': 'utf8mb4',
        }
    }
}
```

### 2. Authentication Configuration (Bible Study)

In Bible Study's `settings.py`, use the main site's user model:

```python
# Point to the main website's CustomUser model
AUTH_USER_MODEL = 'website.CustomUser'

# Use main site's authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'website.backends.EmailAuthBackend',      # If using email login
    'website.backends.CustomUserAuthBackend',  # If using custom backend
]
```

### 3. Import CustomUser Model

Option A: Direct import (if website app is accessible)
```python
from website.models import CustomUser, BibleStudySemester, BibleStudyEnrollment
```

Option B: Copy the model definition if maintaining separate codebases
- Copy `CustomUser` model from main site to Bible Study
- Keep the app label as 'website' to maintain compatibility

### 4. Shared Models

Bible Study can import and use these models from the main site:
- `CustomUser` - The shared user model
- `BibleStudySemester` - Semester definitions created on main site
- `BibleStudyEnrollment` - Enrollment records created when users enroll on main site

Example in Bible Study app:
```python
from website.models import CustomUser, BibleStudySemester, BibleStudyEnrollment

# Get enrolled users for a semester
semester = BibleStudySemester.objects.get(is_active=True)
enrollments = BibleStudyEnrollment.objects.filter(semester=semester)

for enrollment in enrollments:
    user = enrollment.user
    print(f"User: {user.full_name}, Year: {user.yearOfStudy}")
```

### 5. Session & Cookie Configuration (Bible Study)

To allow seamless login between main site and Bible Study, configure shared session:

```python
# .env or settings.py

# Use same session cookie name and path
SESSION_COOKIE_DOMAIN = '.eunccu.org'  # Shared across subdomains
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF configuration
CSRF_COOKIE_DOMAIN = '.eunccu.org'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'https://eunccu.org',
    'https://www.eunccu.org',
    'https://biblestudy.eunccu.org',
]
```

### 6. Environment Variables (Bible Study)

Create `.env` file in Bible Study project:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<same-or-different-key>
DATABASE_ENGINE=mysql
DATABASE_NAME=eunccu_production_db
DATABASE_USER=eunccu_prod_user
DATABASE_PASSWORD=your-db-password
DATABASE_HOST=your-mysql-host.com
ALLOWED_HOSTS=biblestudy.eunccu.org,.eunccu.org
USE_HTTPS=True
```

## Testing the Integration

### 1. Verify Database Connection
```bash
cd /path/to/bible-study
python manage.py dbshell
# If successful, you're connected to the shared database
```

### 2. Run Migrations
```bash
python manage.py migrate
# Should not show new CustomUser migrations (model already exists in main site)
```

### 3. Test User Login
1. Create a user on main site: `https://eunccu.org/`
2. Go to Bible Study: `https://biblestudy.eunccu.org/login/`
3. Log in with the same email/password
4. Should access Bible Study as the same user

### 4. Test Enrollment Data
1. Log in to main site
2. Enroll in Bible Study from main site profile
3. Go to Bible Study app
4. Should see the enrollment in `BibleStudyEnrollment` table
5. Should see user profile with year, residency, etc.

## Grouping Logic (Bible Study Side)

After users enroll from the main site, Bible Study can auto-group them:

```python
from website.models import BibleStudyEnrollment, CustomUser

def assign_bible_study_groups():
    """Auto-assign users to groups based on profile info"""
    semester = BibleStudySemester.objects.get(is_active=True)
    
    # Get all users who enrolled but aren't grouped yet
    ungrouped = BibleStudyEnrollment.objects.filter(
        semester=semester,
        assigned_group__isnull=True
    )
    
    for enrollment in ungrouped:
        user = enrollment.user
        
        # Create group name based on year + hall
        group_name = f"{user.yearOfStudy}yr - {user.hallOfResidence}"
        
        # Get or create group
        group, _ = BibleStudyGroup.objects.get_or_create(
            name=group_name,
            semester=semester
        )
        
        # Assign user to group
        enrollment.assigned_group = group
        enrollment.save()
```

## Data Available from CustomUser

Bible Study can use any of these user fields for grouping/management:

```python
user.email                  # Email address
user.full_name             # Full name
user.phone                 # Phone number
user.registrationNumber    # Student registration #
user.yearOfStudy           # 1, 2, 3, or 4
user.residencyType         # 'hall' or 'off_campus'
user.hallOfResidence       # Hall name (if in hall)
user.offCampusArea         # Area name (if off-campus)
user.completed             # True if profile complete
user.created_at            # Registration date
user.is_active             # Account active status
```

## DNS & Subdomain Setup

1. Create DNS A record for `biblestudy.eunccu.org` pointing to your server
2. Or create CNAME record pointing to `eunccu.org`
3. Wait for DNS propagation (up to 24 hours)
4. Test: `ping biblestudy.eunccu.org`

## Hosting Deployment

### Option A: Same Server
- Bible Study and main site on same server
- Both services point to same database
- Use nginx/Apache to route based on subdomain

### Option B: Separate Servers
- Main site on server A
- Bible Study on server B
- Both connect to shared database on server C
- Database server must be network-accessible from both servers

### Option C: Docker Containers
- Containerize both apps
- Share MySQL database container
- Use shared network for communication

## Troubleshooting

### "AUTH_USER_MODEL refers to model 'website.CustomUser' that has not been installed"
- Ensure `website` app is in `INSTALLED_APPS`
- Check that both apps reference the same database

### Session Not Shared Between Domains
- Verify `SESSION_COOKIE_DOMAIN = '.eunccu.org'`
- Check that both apps use same SECRET_KEY (or set up session sharing)
- Test with browser dev tools → Application → Cookies

### Enrollment Data Not Visible
- Verify database connection is to same host/database
- Run: `python manage.py shell` and check `BibleStudyEnrollment.objects.all()`
- Check database permissions

### Login Fails on Bible Study
- Verify user exists in shared database
- Check password hash is compatible
- Test with main site login first

## Rollback Plan

If integration fails:
1. Bible Study reverts to standalone database
2. No changes to main site needed
3. Can retry integration later

## Next Steps

After successful integration:
1. Set up automated backups for shared database
2. Configure monitoring/alerts for both services
3. Set up user support process for account issues
4. Create admin documentation for managing both apps
5. Plan capacity for increased database load

## Contact & Support

For integration issues:
- Check this guide first
- Review Bible Study app's documentation
- Verify database credentials and connectivity
- Check application logs on both services

---

**Last Updated:** 2026-08-14
**Status:** Ready for Integration
