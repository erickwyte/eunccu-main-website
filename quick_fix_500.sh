#!/bin/bash
# IMMEDIATE FIX FOR ALL 500 ERRORS
# Fixes: Gallery, Devotions, Ministries, Leadership, Events, Home, and more
# Run this on your production server NOW

echo "=========================================="
echo "FIXING ALL 500 ERRORS"
echo "=========================================="
echo ""
echo "Affected pages:"
echo "  ❌ /gallery/"
echo "  ❌ /devotions/"
echo "  ❌ /ministries/"
echo "  ❌ /leadership/"
echo "  ❌ /events/"
echo "  ❌ / (Home)"
echo ""

# Activate virtual environment
echo "[1/5] Activating virtual environment..."
source 3.13/bin/activate

# Check database connection
echo "[2/5] Checking database connection..."
python manage.py shell -c "from django.db import connection; connection.cursor().execute('SELECT 1'); print('✅ Database OK')"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed!"
    echo "Check your .env file DATABASE settings:"
    cat .env | grep DATABASE
    exit 1
fi

# Run migrations - FIXES MISSING TABLES
echo "[3/5] Running database migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Migration failed!"
    exit 1
fi

# Collect static files
echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo "⚠️  Static files collection had issues (non-critical)"
fi

# Run diagnostic
echo "[5/5] Running diagnostic check..."
python debug_500_errors.py

echo ""
echo "=========================================="
echo "✅ FIXES COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart your application:"
echo "   - If using Gunicorn: pkill -f gunicorn && gunicorn union.wsgi:application --bind 0.0.0.0:8000 --workers 4"
echo "   - If using cPanel: Restart via cPanel console"
echo ""
echo "2. Test these pages:"
echo "   - https://eunccu.org/"
echo "   - https://eunccu.org/gallery/"
echo "   - https://eunccu.org/devotions/"
echo "   - https://eunccu.org/ministries/"
echo "   - https://eunccu.org/leadership/"
echo "   - https://eunccu.org/events/"
echo ""
echo "If still seeing 500 errors, run:"
echo "   python debug_500_errors.py"
echo ""
