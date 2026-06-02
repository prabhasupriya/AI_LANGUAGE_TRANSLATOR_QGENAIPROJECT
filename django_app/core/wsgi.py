import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Explicitly append paths so Django never loses track of the core module attributes
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# This creates the exact application callable attribute Django is demanding
application = get_wsgi_application()

# Global fallback mapping to bypass any strict string parsing errors
wsgi = application