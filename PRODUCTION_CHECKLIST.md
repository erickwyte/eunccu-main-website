# Production Deployment - Pre-Flight Checklist

## ✅ COMPLETED PREPARATIONS

### Code & Configuration
- [x] All production apps re-enabled
  - ✅ Jazzmin (modern admin interface)
  - ✅ CKEditor 5 (rich text editing)
  - ✅ Django Extensions
- [x] Test setup files removed
  - ✅ setup_test_admin.py
  - ✅ setup_ui_test_data.py
  - ✅ verify_enrollment.py
  - ✅ Test data cleanup
- [x] Production configuration verified
  - ✅ WhiteNoise for static files
  - ✅ Environment-based settings
  - ✅ MySQL configuration tested
  - ✅ Email settings configured

### Documentation Created
- [x] `.env.example` - All production environment variables documented
- [x] `DEPLOYMENT.md` - Complete deployment guide (100+ checklist items)
- [x] `BIBLE_STUDY_INTEGRATION.md` - Bible Study integration guide
- [x] `README_PRODUCTION.md` - Quick reference guide

### Testing & Verification
- [x] Django system checks passed
- [x] All migrations applied
- [x] Bible Study enrollment tested end-to-end
- [x] Core features verified locally

### Database
- [x] All migrations created and tested
- [x] Models include:
  - CustomUser (with all profile fields)
  - BibleStudySemester
  - BibleStudyEnrollment
  - Events, Gallery, Testimonies, Devotions, etc.

---

## 📋 WHAT YOU NEED TO DO BEFORE GOING LIVE

### Step 1: Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and put it in your `.env` as `SECRET_KEY=`

### Step 2: Set Up Database
On your hosting provider:
1. Create MySQL database: `eunccu_production_db`
2. Create MySQL user: `eunccu_prod_user`
3. Grant all privileges on database to user
4. Note the DATABASE_HOST (should be provided by hosting)

### Step 3: Create .env File
On your server, create `.env` file with:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<from-step-1>
DATABASE_NAME=eunccu_production_db
DATABASE_USER=eunccu_prod_user
DATABASE_PASSWORD=<your-strong-password>
DATABASE_HOST=<your-mysql-host>
DATABASE_PORT=3306
ALLOWED_HOSTS=eunccu.org,www.eunccu.org
CSRF_TRUSTED_ORIGINS=https://eunccu.org,https://www.eunccu.org
EMAIL_HOST_USER=noreply@eunccu.org
EMAIL_HOST_PASSWORD=<your-email-password>
USE_HTTPS=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Create Admin User
```bash
python manage.py createsuperuser
```

### Step 8: Start Application
Use Gunicorn (recommended for production):
```bash
gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

---

## 🔍 POST-DEPLOYMENT VERIFICATION

After deployment, test these:

### Basic Functionality
- [ ] Homepage loads: `https://eunccu.org/`
- [ ] Admin accessible: `https://eunccu.org/admin/`
- [ ] Login works: `https://eunccu.org/login/`
- [ ] User can view profile: `https://eunccu.org/profile/`
- [ ] "Enroll for Bible Study" button appears on profile
- [ ] Enrollment button works (creates record when clicked)

### Security
- [ ] HTTP redirects to HTTPS
- [ ] HSTS headers present (check: `curl -i https://eunccu.org | grep Strict`)
- [ ] Admin login is secure

### Static Files
- [ ] CSS loads properly (no styling issues)
- [ ] Images display
- [ ] JavaScript works

### Email
- [ ] Test email sending (register new user, check inbox)
- [ ] Check hosting provider's email logs

### Database
- [ ] Can create new accounts
- [ ] Profiles save correctly
- [ ] Enrollment records persist

---

## 📦 DEPLOYMENT OPTIONS

### Option 1: PythonAnywhere
1. Create account at pythonanywhere.com
2. Upload code
3. Create virtual env
4. Link to MySQL database
5. Configure web app
6. Enable SSL (free)
7. Done! ✅

### Option 2: Heroku
1. Create Heroku app
2. Add Heroku Postgres add-on
3. Push code with git
4. Set environment variables
5. Enable SSL (automatic)
6. Done! ✅

### Option 3: Custom VPS (DigitalOcean, Linode, AWS, etc.)
1. Create Ubuntu VM
2. Install Python, MySQL, Nginx
3. Create virtual env
4. Upload code
5. Configure Gunicorn + Nginx
6. Set up SSL with Let's Encrypt
7. Done! ✅

### Option 4: Docker
1. Build Docker image
2. Push to container registry
3. Deploy to hosting (Google Cloud Run, AWS ECS, etc.)
4. Done! ✅

---

## 🐛 COMMON DEPLOYMENT ISSUES

### Issue: "No module named 'website'"
**Solution:** Ensure virtual environment is activated and requirements.txt installed

### Issue: Static files not loading
**Solution:** Run `python manage.py collectstatic --noinput`

### Issue: Database connection error
**Solution:** 
- Check DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
- Verify database server is running
- Test connection: `mysql -h <HOST> -u <USER> -p`

### Issue: Email not working
**Solution:**
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Check hosting provider's email settings
- Test SMTP connection manually

### Issue: Admin interface styling broken
**Solution:** Run collectstatic again and clear browser cache

See **DEPLOYMENT.md** for more detailed troubleshooting.

---

## 📚 DOCUMENTATION FILES

Read these in order:

1. **README_PRODUCTION.md** - Overview and quick start
2. **DEPLOYMENT.md** - Detailed deployment steps + checklist (⭐ MOST IMPORTANT)
3. **BIBLE_STUDY_INTEGRATION.md** - For later when connecting Bible Study

---

## ✅ PRODUCTION READINESS SUMMARY

| Component | Status | Notes |
|-----------|--------|-------|
| Django Setup | ✅ Ready | 4.2.29 LTS with Python 3.14 patch |
| Database | ✅ Ready | All migrations created and tested |
| Authentication | ✅ Ready | Email + custom backends working |
| Bible Study | ✅ Ready | Enrollment end-to-end tested |
| Static Files | ✅ Ready | WhiteNoise configured |
| Admin UI | ✅ Ready | Jazzmin + native admin |
| Email | ✅ Ready | SMTP configured |
| Security | ✅ Ready | HTTPS, HSTS, CSRF, XSS protection |
| Tests | ✅ Passing | All core features verified |
| Documentation | ✅ Complete | Deployment + Integration guides |

**Overall Status: 🟢 PRODUCTION READY**

---

## 🚀 DEPLOYMENT TIMELINE

**Week 1:**
- [ ] Choose hosting platform
- [ ] Get database credentials
- [ ] Deploy main site
- [ ] Test all features
- [ ] Set up monitoring

**Week 2-4:**
- [ ] Promote to users
- [ ] Monitor performance
- [ ] Fix any issues

**Month 2:**
- [ ] Prepare Bible Study integration
- [ ] Set up biblestudy.eunccu.org subdomain
- [ ] Deploy Bible Study app

---

## 📞 SUPPORT

If you encounter issues:

1. Check the relevant documentation file
2. Review Django logs
3. Test database connectivity
4. Verify environment variables
5. Check hosting provider's dashboard

---

**Status:** READY FOR PRODUCTION DEPLOYMENT ✅  
**Date:** 2026-08-14  
**Next Step:** Follow DEPLOYMENT.md
