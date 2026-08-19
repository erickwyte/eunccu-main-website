# EUNCCU Main Website - Production Ready

This is the main EUNCCU website, now prepared for production deployment.

## Project Status: ✅ PRODUCTION READY

All core features are tested and ready to host:
- User authentication and profiles
- Bible Study enrollment system
- Event management
- Gallery system
- Testimonies with admin approval
- Devotions
- User management dashboard
- Admin interface (Jazzmin)

## Quick Start for Deployment

### 1. Prerequisites
- Python 3.13+
- MySQL 10.6 or later
- Virtual environment
- pip

### 2. Installation

```bash
# Clone/extract the project
cd eunccu-main-site

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy and fill `.env.example`:
```bash
cp .env.example .env
# Edit .env with your production values
```

Key variables to set:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-new-key>
DATABASE_NAME=eunccu_prod_db
DATABASE_USER=eunccu_prod_user
DATABASE_PASSWORD=<strong-password>
DATABASE_HOST=<your-mysql-host>
EMAIL_HOST_USER=noreply@eunccu.org
EMAIL_HOST_PASSWORD=<your-email-password>
ALLOWED_HOSTS=eunccu.org,www.eunccu.org
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Start Application

**Development (testing only):**
```bash
python manage.py runserver 0.0.0.0:8000
```

**Production (using Gunicorn):**
```bash
gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Features & Components

### User Management
- Email-based authentication
- Custom user model with profile fields
- Role-based access control
- Admin dashboard for user management

### Bible Study Integration
- Semester management
- Automatic enrollment tracking
- Profile-based grouping (handled by Bible Study app)
- Enrollment from user profile page

### Content Management
- Events with date/time management
- Gallery with image uploads
- Devotions with rich text
- Testimonies with admin approval
- News & announcements

### Admin Interface
- Jazzmin admin dashboard (modern UI)
- Full CRUD operations
- User management
- Content moderation

## Key Files

### Configuration
- `union/settings.py` - Main Django settings
- `.env` - Environment variables (production)
- `union/test_settings.py` - Test configuration

### Models
- `website/models.py` - All data models
  - CustomUser (profiles, residency info)
  - BibleStudySemester
  - BibleStudyEnrollment
  - Events, Gallery, Devotions, Testimonies, etc.

### Views & URLs
- `website/views.py` - Main application logic
- `website/urls.py` - URL routing
- `auth_utils/views.py` - Authentication views

### Static & Media
- `static/` - CSS, JS, images (development)
- `staticfiles/` - Collected static files (production)
- `media/` - User uploads (images, files)

## Documentation

**Read these before deploying:**

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Step-by-step deployment guide
   - Environment setup
   - Database configuration
   - Post-deployment checks
   - Troubleshooting

2. **[BIBLE_STUDY_INTEGRATION.md](./BIBLE_STUDY_INTEGRATION.md)** - Bible Study subdomain setup
   - Shared database configuration
   - Authentication setup
   - Grouping logic
   - Testing integration

## Environment Variables

All required environment variables are documented in `.env.example`. Key categories:

- **ENVIRONMENT & DEBUG** - Set to production/False
- **SECURITY** - SSL, HSTS, CSRF settings
- **DATABASE** - MySQL connection
- **EMAIL** - SMTP configuration
- **SITE** - Domain and URL settings
- **API KEYS** - YouTube, Google Drive (optional)

## Database Schema

Core tables:
- `website_customuser` - User profiles
- `website_biblestudysemester` - Semester definitions
- `website_biblestudyenrollment` - User enrollments
- `website_event` - Events
- `website_gallery` - Photo gallery
- `website_devotion` - Daily devotions
- `website_testimony` - User testimonies
- `auth_group` - User roles/permissions

## Security

Production security features enabled:
- HTTPS/SSL redirect
- HSTS headers
- Secure cookies
- CSRF protection
- XSS prevention
- SQL injection protection (via ORM)
- Strong password requirements

## Monitoring & Maintenance

### Regular Tasks
- Monitor application error logs
- Check database performance
- Verify SSL certificate validity
- Test email delivery
- Monitor disk/memory usage

### Backups
- Daily database backups (configure on your host)
- Media files backup
- Static files can be regenerated

### Updates
- Keep Django and dependencies updated
- Monitor security advisories
- Test updates in development first

## API Endpoints

### Public Pages
- `/` - Homepage
- `/events/` - Events listing
- `/gallery/` - Photo gallery
- `/devotions/` - Daily devotions
- `/about/` - About page
- `/contact/` - Contact form

### Authentication
- `/login/` - Login page
- `/register/` - Registration
- `/profile/` - User profile
- `/logout/` - Logout

### Bible Study
- `/profile/enroll-bible-study/` - Enroll in Bible Study

### Admin
- `/admin/` - Django admin interface
- `/admin/jazzmin/` - Modern admin dashboard

## Troubleshooting

**See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting guide.**

Common issues:
- Static files not loading → Run `collectstatic`
- Database errors → Check DATABASE_* env vars
- Email not sending → Verify EMAIL_* settings
- Login issues → Check user exists in database
- Page not found → Check URL routing in `website/urls.py`

## Support & Contact

For deployment assistance:
1. Review the documentation files
2. Check application logs
3. Verify environment variables
4. Test database connectivity
5. Review hosting provider's Django guide

## Version Information

- Django: 4.2.29
- Python: 3.13+ (with 3.14 compatibility patch)
- Database: MySQL 10.6+
- Static Files: WhiteNoise
- Admin UI: Jazzmin
- Rich Text: CKEditor 5

## Production Checklist

Before going live:
- [ ] All env variables set
- [ ] Database migrations run
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] Email configured and tested
- [ ] Database backups configured
- [ ] Superuser created
- [ ] Admin interface tested
- [ ] Homepage loads
- [ ] Login works
- [ ] Profile enrollment tested

## Next Steps

### Immediate (After Deployment)
1. Create admin accounts
2. Add initial content (events, devotions)
3. Test email notifications
4. Monitor logs for errors

### Short Term (1-2 weeks)
1. Promote to users
2. Gather user feedback
3. Fix any issues

### Medium Term (Before Bible Study Integration)
1. Verify enrollment data quality
2. Plan Bible Study subdomain
3. Prepare integration guide for Bible Study team

### Long Term (Bible Study Integration)
1. Deploy Bible Study on subdomain
2. Configure shared database
3. Test cross-app authentication
4. Monitor performance

---

**Status:** Production Ready ✅  
**Last Updated:** 2026-08-14  
**Prepared by:** AI Assistant
