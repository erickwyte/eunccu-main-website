"""
WSGI config for EUNCCU System application.
"""

import os
import sys
import site

# ============================================================================
# VIRTUAL ENVIRONMENT CONFIGURATION
# ============================================================================
VENV_PATH = '/home1/eunccuor/virtualenv/public_html/System/3.13'
PYTHON_VERSION = '3.13'
APP_PATH = '/home1/eunccuor/sampleweb.eunccu.org/System'
# Add the site-packages of the virtualenv to sys.path
site_packages_path = os.path.join(VENV_PATH, f'lib/python{PYTHON_VERSION}/site-packages')
if os.path.exists(site_packages_path):
    site.addsitedir(site_packages_path)
else:
    # Fallback: try to find the site-packages directory
    for path in os.listdir(os.path.join(VENV_PATH, 'lib')):
        if path.startswith('python'):
            site_packages_path = os.path.join(VENV_PATH, f'lib/{path}/site-packages')
            if os.path.exists(site_packages_path):
                site.addsitedir(site_packages_path)
                break

# Add the virtualenv's bin directory to sys.path
bin_path = os.path.join(VENV_PATH, 'bin')
if bin_path not in sys.path:
    sys.path.append(bin_path)

# ============================================================================
# APPLICATION PATH CONFIGURATION
# ============================================================================
# Add the app directory to the PYTHONPATH
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'union.settings')

# ============================================================================
# WSGI APPLICATION
# ============================================================================
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    with open(os.path.join(APP_PATH, 'wsgi_error.log'), 'a') as f:
        f.write(f"WSGI Application Error: {str(e)}\n")
        f.write(traceback.format_exc())
    raise
