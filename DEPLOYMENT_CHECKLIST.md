# 🚀 DEPLOYMENT CHECKLIST - FINAL VERIFICATION

## ✅ COMPLETED FIXES IN THIS SESSION

### Code & Configuration Fixes
- [x] Fixed duplicate static files (Bootstrap, FontAwesome)
- [x] Fixed CSS image path references in dataTables.bootstrap.css
- [x] Fixed slow network font warnings
  - [x] Removed Font Awesome from CDN
  - [x] Using local Font Awesome v5.9.0 with v4 compatibility
  - [x] Added font preloading
  - [x] Added font-display: swap

### Documentation Created
- [x] `debug_500_errors.py` - Comprehensive diagnostic script
- [x] `quick_fix_500.sh` - Automated fix script
- [x] `500_ERROR_COMPLETE_ANALYSIS.md` - Detailed page analysis
- [x] `FIX_500_ERRORS.md` - Full troubleshooting guide
- [x] `QUICK_FIX_REFERENCE.md` - Quick reference

---

## 🚨 CRITICAL: Before Deployment

### ⚠️ STEP 1: Run Migrations on Production
**THIS MUST BE DONE BEFORE GOING LIVE**

```bash
ssh user@eunccu.org
cd /path/to/System
source 3.13/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

Without this step, you'll get 500 errors on ALL pages that query the database.

### ⚠️ STEP 2: Verify Environment Variables

On production server, check `.env` file:
```bash
cat .env
```

Must contain:
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<your-generated-key>
DATABASE_NAME=eunccu_production_db
DATABASE_USER=eunccu_prod_user
DATABASE_PASSWORD=<strong-password>
DATABASE_HOST=localhost (or your MySQL host)
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

### ⚠️ STEP 3: Verify Database Setup

```bash
mysql -h localhost -u eunccu_prod_user -p
# Enter password

# Inside MySQL:
SHOW DATABASES;
USE eunccu_production_db;
SHOW TABLES;
EXIT;
```

Should show 20+ tables including:
- `auth_user`
- `website_image`
- `website_devotion`
- `website_event`
- `website_ministry`
- `website_exec`
- `website_leader`
- etc.

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### Server Setup
- [ ] Virtual environment created: `python -m venv 3.13`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] MySQL database created: `eunccu_production_db`
- [ ] MySQL user created: `eunccu_prod_user` with all privileges

### Configuration
- [ ] `.env` file created with all variables
- [ ] `SECRET_KEY` generated and set
- [ ] `DEBUG=False` in `.env`
- [ ] Database credentials verified and working

### Database
- [ ] Migrations run: `python manage.py migrate` ✅
- [ ] Static files collected: `python manage.py collectstatic --noinput` ✅
- [ ] Admin superuser created: `python manage.py createsuperuser`

### Code Quality
- [ ] `python manage.py check` passes
- [ ] No unresolved imports
- [ ] All settings are environment-based

### Static Files & Assets
- [ ] [x] Bootstrap files cleaned up (removed duplicates from static/js/)
- [ ] [x] FontAwesome switched to local (removed CDN)
- [ ] [x] CSS image paths fixed (dataTables)
- [ ] [x] Font preloading added
- [ ] [x] Staticfiles directory cleared

### Testing (Local)
- [ ] Home page loads: `/`
- [ ] Gallery loads: `/gallery/`
- [ ] Devotions load: `/devotions/`
- [ ] Ministries load: `/ministries/`
- [ ] Leadership loads: `/leadership/`
- [ ] Events load: `/events/`
- [ ] Login works: `/login/`
- [ ] No console errors in browser

### Security
- [ ] HTTPS enabled (SSL certificate installed)
- [ ] SECURE_SSL_REDIRECT=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SECURE_HSTS_SECONDS=31536000
- [ ] Admin interface accessible only over HTTPS

### Monitoring
- [ ] Error logging configured
- [ ] Email alerts for errors configured
- [ ] Log files have proper permissions

---

## 🎯 FINAL DEPLOYMENT STEPS

### Step 1: Upload Code
```bash
scp -r System/ user@eunccu.org:/path/to/destination/
```

### Step 2: Setup on Server
```bash
ssh user@eunccu.org

# Navigate to project
cd /path/to/System

# Create virtual environment
python -m venv 3.13
source 3.13/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env with your production values
nano .env
```

### Step 3: Initialize Database
```bash
# Create database (if not exists)
mysql -u root -p << EOF
CREATE DATABASE eunccu_production_db;
CREATE USER 'eunccu_prod_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON eunccu_production_db.* TO 'eunccu_prod_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin user
python manage.py createsuperuser
```

### Step 4: Run Diagnostic
```bash
python debug_500_errors.py
```

Should show all ✅ (green checks)

### Step 5: Start Application
```bash
# Using Gunicorn (Recommended)
gunicorn union.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

# OR use a process manager like Supervisor (recommended for production)
```

### Step 6: Configure Reverse Proxy
Setup Nginx or Apache to proxy to Gunicorn:
```nginx
server {
    listen 443 ssl http2;
    server_name eunccu.org www.eunccu.org;
    
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /path/to/System/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/System/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name eunccu.org www.eunccu.org;
    return 301 https://$server_name$request_uri;
}
```

### Step 7: Test Live Site
```bash
# From your local machine
curl -I https://eunccu.org/
curl -I https://eunccu.org/gallery/
curl -I https://eunccu.org/devotions/
curl -I https://eunccu.org/ministries/
```

All should return `200 OK` (not 500)

### Step 8: Monitor Logs
```bash
tail -f /path/to/logs/error.log
tail -f /path/to/logs/access.log
```

---

## ⚠️ COMMON DEPLOYMENT ISSUES

### Issue: 500 Errors After Deployment
```bash
# Run diagnostic
python debug_500_errors.py

# Most likely: Migrations not run
python manage.py migrate
```

### Issue: Static Files Not Loading (404)
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify permissions
chmod -R 755 staticfiles/
```

### Issue: Database Connection Failed
```bash
# Check .env DATABASE settings
grep DATABASE .env

# Verify MySQL user and password
mysql -u eunccu_prod_user -p -e "SELECT 1;"

# Verify database exists
mysql -u root -p -e "SHOW DATABASES;"
```

### Issue: Fonts Still Loading from CDN
✅ Already fixed - Font Awesome now loads locally from:
- `static/vendor/fontawesome-free/css/v4-shims.min.css`

Check in browser DevTools Network tab - should be 200 OK from `/static/vendor/...`

---

## 📊 DEPLOYMENT SUCCESS CHECKLIST

After deployment, verify:

- [ ] Homepage loads without errors
- [ ] Gallery page displays images
- [ ] Devotions page shows devotions
- [ ] Ministries page loads
- [ ] Leadership page loads
- [ ] Events display correctly
- [ ] Login functionality works
- [ ] Admin interface accessible at `/admin/`
- [ ] No 500 errors in browser console
- [ ] Static files load (CSS, JS, images)
- [ ] Fonts load without slow network warnings
- [ ] HTTPS works (lock icon in browser)
- [ ] Redirect from HTTP to HTTPS works
- [ ] Email notifications work (if configured)

---

## 📞 SUPPORT TOOLS

If issues arise after deployment:

1. **Check logs:**
   ```bash
   python debug_500_errors.py
   ```

2. **Quick diagnostics:**
   ```bash
   python manage.py check
   ```

3. **Database verification:**
   ```bash
   python manage.py shell
   from website.models import Image, Event, Devotion
   print(f"Images: {Image.objects.count()}")
   print(f"Events: {Event.objects.count()}")
   print(f"Devotions: {Devotion.objects.count()}")
   exit()
   ```

---

## ✅ PROJECT STATUS

**Code Quality:** ✅ Ready
- All duplicates removed
- All paths fixed
- Font loading optimized

**Documentation:** ✅ Ready
- Deployment guide complete
- Troubleshooting tools created
- Diagnostic scripts ready

**Configuration:** ⚠️ Must Complete
- [ ] Set production environment variables
- [ ] Create/verify MySQL database
- [ ] Run migrations on production
- [ ] Verify SSL certificate installed

**Security:** ✅ Configured
- HTTPS enforced
- HSTS headers set
- Secure cookies configured

---

## 🎬 READY FOR DEPLOYMENT?

✅ **Code is ready** - All fixes applied locally

⚠️ **Production setup remaining** - Need to:
1. Create production database and user
2. Upload code and create .env
3. Run `python manage.py migrate`
4. Configure reverse proxy (Nginx/Apache)
5. Start Gunicorn with process manager

**Estimated time:** 30-45 minutes for setup

**Questions?** Check the troubleshooting guides!
