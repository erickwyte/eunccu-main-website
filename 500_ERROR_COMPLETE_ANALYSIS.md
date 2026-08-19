# 500 ERROR ANALYSIS - All Affected Pages

## AFFECTED PAGES (Requires Database Queries)

### 1. **Gallery Page**
- **URL**: `/gallery/`
- **View**: `GalleryView`
- **Models Queried**: 
  - ✓ Image (table: `website_image`)
- **Error**: 500 if `website_image` table missing

### 2. **Devotions Page**
- **URL**: `/devotions/`
- **View**: `devotion_list()`
- **Models Queried**:
  - ✓ Devotion (table: `website_devotion`)
- **Error**: 500 if `website_devotion` table missing

### 3. **Devotion Detail Page**
- **URL**: `/devotions/<slug>/`
- **View**: `devotion_detail()`
- **Models Queried**:
  - ✓ Devotion (table: `website_devotion`)
- **Error**: 500 if `website_devotion` table missing

### 4. **Ministries Page** ⚠️ (Currently Erroring)
- **URL**: `/ministries/`
- **View**: `MinistriesView`
- **Models Queried**:
  - ✓ Ministry (table: `website_ministry`)
  - ✓ Eteam (table: `website_eteam`)
  - ✓ Class (table: `website_class`)
  - ✓ SpecialCommittee (table: `website_specialcommittee`)
- **Error**: 500 if ANY of these tables missing

### 5. **Leadership Page**
- **URL**: `/leadership/`
- **View**: `LeadershipView`
- **Models Queried**:
  - ✓ Exec (table: `website_exec`)
  - ✓ Leader (table: `website_leader`)
- **Error**: 500 if either table missing

### 6. **Events Page**
- **URL**: `/events/`
- **View**: `events()`
- **Models Queried**:
  - ✓ Event (table: `website_event`)
- **Error**: 500 if table missing

### 7. **Past Events Page**
- **URL**: `/events/past/`
- **View**: `all_past_events()`
- **Models Queried**:
  - ✓ Event (table: `website_event`)
- **Error**: 500 if table missing

### 8. **Event Detail Page**
- **URL**: `/events/<id>/`
- **View**: `event_detail()`
- **Models Queried**:
  - ✓ Event (table: `website_event`)
- **Error**: 500 if table missing

### 9. **Home Page**
- **URL**: `/`
- **View**: `index()`
- **Models Queried**:
  - ✓ SemesterTheme (table: `website_semestertheme`)
  - ✓ BibleStudySemester (table: `website_biblestudysemester`)
  - ✓ Devotion (table: `website_devotion`)
  - ✓ Event (table: `website_event`)
  - ✓ Testimony (table: `website_testimony`)
- **Error**: 500 if ANY of these tables missing

### 10. **Submit Testimony Page**
- **URL**: `/testimonies/submit/`
- **View**: `submit_testimony()`
- **Models Queried**:
  - ✓ Testimony (table: `website_testimony`)
- **Error**: 500 if table missing

### 11. **Profile Page** (Logged-in users)
- **URL**: `/profile/`
- **View**: `ProfileView`
- **Models Queried**:
  - ✓ BibleStudyEnrollment (table: `website_biblestudyenrollment`)
- **Error**: 500 if table missing

### 12. **User Manager Dashboard** (Admin only)
- **URL**: `/user-manager/`
- **View**: `UserManagerDashboardView`
- **Models Queried**:
  - ✓ CustomUser (table: `auth_user`)
- **Error**: 500 if table missing

---

## ALL REQUIRED TABLES

Run this SQL to check all required tables exist:

```sql
-- Check all required tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA='eunccu_production_db' 
AND TABLE_NAME IN (
  'website_image',
  'website_devotion',
  'website_ministry',
  'website_eteam',
  'website_class',
  'website_specialcommittee',
  'website_exec',
  'website_leader',
  'website_event',
  'website_testimony',
  'website_semestertheme',
  'website_biblestudysemester',
  'website_biblestudyenrollment',
  'auth_user'
)
ORDER BY TABLE_NAME;
```

Expected output: 14 rows

---

## DIAGNOSIS: Which Tables Are Missing?

Run on your server:
```bash
python debug_500_errors.py
```

This will tell you EXACTLY which tables are missing.

---

## THE FIX

### Option 1: Run Migrations (BEST - Fixes All)
```bash
# SSH to server
cd /path/to/System
source 3.13/bin/activate

# Run migrations to create all tables
python manage.py migrate

# Verify
python debug_500_errors.py
```

### Option 2: Check Migration History
```bash
# See which migrations have been run
python manage.py showmigrations
```

If all migrations are marked with ✓, but tables still missing:
```bash
# Re-run all migrations
python manage.py migrate --run-syncdb
```

### Option 3: Fresh Database (Caution: Deletes all data!)
```bash
# ONLY if you have backups or are testing
mysql> DROP DATABASE eunccu_production_db;
mysql> CREATE DATABASE eunccu_production_db;
mysql> GRANT ALL PRIVILEGES ON eunccu_production_db.* TO 'eunccu_prod_user'@'localhost';

# Then run migrations
python manage.py migrate
```

---

## AFTER APPLYING FIXES

1. **Collect static files** (recommended):
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Restart application**:
   ```bash
   # If using Gunicorn
   pkill -f gunicorn
   gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4
   
   # Or restart via cPanel
   ```

3. **Test all affected pages**:
   - https://eunccu.org/ (Home)
   - https://eunccu.org/gallery/
   - https://eunccu.org/devotions/
   - https://eunccu.org/ministries/ ⚠️
   - https://eunccu.org/leadership/
   - https://eunccu.org/events/

4. **Monitor for errors**:
   ```bash
   tail -f /path/to/logs/error.log
   ```

---

## SUMMARY TABLE

| Page | URL | Model | Table | Status |
|------|-----|-------|-------|--------|
| Gallery | `/gallery/` | Image | `website_image` | ✓ Created |
| Devotions | `/devotions/` | Devotion | `website_devotion` | ✓ Created |
| Ministries | `/ministries/` | Ministry, Eteam, Class, SpecialCommittee | Multiple | ✓ Created |
| Leadership | `/leadership/` | Exec, Leader | Multiple | ✓ Created |
| Events | `/events/` | Event | `website_event` | ✓ Created |
| Home | `/` | Multiple | Multiple | ✓ Created |
| Profiles | `/profile/` | BibleStudyEnrollment | `website_biblestudyenrollment` | ✓ Created |

All tables created by running: `python manage.py migrate`
