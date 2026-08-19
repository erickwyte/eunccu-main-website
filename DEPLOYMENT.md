# EUNCCU Main Website - Production Deployment Checklist

## Pre-Deployment (Local)

### Code & Configuration
- [ ] All production apps are enabled in `union/settings.py`
- [ ] Test files removed (`setup_*.py`, `verify_*.py`)
- [ ] `.env.example` created with all required variables
- [ ] No hardcoded secrets in code
- [ ] `DEBUG = False` in production
- [ ] All migrations committed to version control

### Database
- [ ] All migrations applied to local test database
- [ ] Database connection tested with MySQL
- [ ] No stale test data remaining

### Testing
- [ ] Run full test suite: `python manage.py test`
- [ ] Check for any warnings: `python manage.py check`
- [ ] Test all critical flows (login, profile, enrollment)

---

## Hosting Setup

### Environment Variables
Set these on your hosting platform:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generate-new-random-key>
DATABASE_ENGINE=mysql
DATABASE_NAME=eunccu_prod_db
DATABASE_USER=<your-db-user>
DATABASE_PASSWORD=<your-db-password>
DATABASE_HOST=<your-db-host>
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-email-password>
ALLOWED_HOSTS=eunccu.org,www.eunccu.org
USE_HTTPS=True
```

### Hosting Platform Setup
- [ ] Server has Python 3.13+ installed
- [ ] MySQL/MariaDB 10.6+ available and accessible
- [ ] Virtual environment created and requirements installed
- [ ] Static file serving configured (WhiteNoise handles this)
- [ ] Media files directory created and writable
- [ ] Logs directory created and writable
- [ ] SSL/HTTPS certificate installed

---

## Initial Deployment

### Database
```bash
# 1. SSH into server
# 2. Activate virtual environment
source venv/bin/activate

# 3. Run migrations
python manage.py migrate

# 4. Create superuser (optional - can do via API later)
python manage.py createsuperuser
```

### Static Files
```bash
# Collect all static files to STATIC_ROOT
python manage.py collectstatic --noinput
```

### Application
```bash
# If using Gunicorn:
gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4

# If using uWSGI:
uwsgi --http :8000 --wsgi-file union/wsgi.py --master --processes 4 --threads 2
```

---

## Post-Deployment Verification

### Basic Checks
- [ ] Homepage loads: `https://eunccu.org/`
- [ ] Admin accessible: `https://eunccu.org/admin/`
- [ ] Login works: `https://eunccu.org/login/`
- [ ] Profile page accessible (when logged in)
- [ ] Bible Study enrollment button visible (when semester is active)

### Security Checks
- [ ] HTTPS redirect works (HTTP → HTTPS)
- [ ] HSTS headers present
- [ ] No sensitive data in error pages
- [ ] CSRF protection enabled
- [ ] Session cookies are secure

### Email Functionality
- [ ] Test email sending (user registration email)
- [ ] Check email logs for errors

### Static Files
- [ ] CSS/JS files load properly
- [ ] Images display correctly
- [ ] Static file paths work in production

### Database
- [ ] Can create new user accounts
- [ ] Can log in successfully
- [ ] Profile data persists
- [ ] Bible Study enrollment creates records

---

## Production Monitoring

### Logs to Monitor
- [ ] Application error logs
- [ ] Database connection errors
- [ ] Email delivery failures
- [ ] Static file serving errors

### Health Checks (Set up automated monitoring)
- [ ] Homepage responds with 200 status
- [ ] Admin login page accessible
- [ ] Database connection is stable
- [ ] Disk space adequate
- [ ] Memory usage normal

### Backups
- [ ] Daily database backups configured
- [ ] Media files backup strategy in place
- [ ] Backup retention policy set (e.g., keep 30 days)

---

## Bible Study Integration (Later)

When ready to connect Bible Study subdomain:

- [ ] Create `biblestudy.eunccu.org` subdomain
- [ ] Point subdomain to same server/Docker container
- [ ] Update Bible Study `settings.py` with shared database credentials
- [ ] Set `AUTH_USER_MODEL = 'website.CustomUser'`
- [ ] Run Bible Study migrations
- [ ] Test login: main site → Bible Study subdomain
- [ ] Verify enrollment data syncs between apps
- [ ] Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS if needed

---

## Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput --clear
```

### Database Connection Issues
- Check DATABASE_HOST is correct
- Verify DATABASE_USER has proper permissions
- Ensure firewall allows connections from app server

### Email Not Sending
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Check email service provider logs
- Ensure SMTP port is open (usually 465 for SSL)

### 502/503 Errors
- Check application server is running
- Check application logs for errors
- Verify database connectivity

---

## Deployment Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Check configuration
python manage.py check

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Start development server (testing only)
python manage.py runserver 0.0.0.0:8000

# Start production server with Gunicorn
gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

---

## Contact & Support

For issues during deployment:
1. Check application logs first
2. Review this checklist for missed steps
3. Verify all environment variables are set
4. Test database connectivity separately
5. Check hosting provider's documentation

---

**Last Updated:** 2026-08-14
**Status:** Production Ready
